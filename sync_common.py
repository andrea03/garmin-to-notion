import os
import json
import random
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from notion_client import Client as NotionClient
from notion_client.errors import APIResponseError

class RateLimitedNotionClient(NotionClient):
    """Pace all sync requests and retry explicit Notion throttling responses."""

    def request(self, path, method, query=None, body=None, auth=None):
        for attempt in range(6):
            # This sync is sequential. Include reads and writes in the same budget.
            time.sleep(0.4)
            try:
                return super().request(path, method, query, body, auth)
            except APIResponseError as error:
                reason = json.loads(error.body).get("additional_data", {}).get("rate_limit_reason")
                if (
                    error.status not in (429, 529)
                    or reason == "public_api_request_blocked"
                    or attempt == 5
                ):
                    raise
                try:
                    retry_after = max(0, int(error.headers.get("Retry-After", "0")))
                except ValueError:
                    retry_after = 0
                delay = max(retry_after, 2 ** attempt) + random.uniform(0, 0.25)
                print(f"Notion rate limited; waiting {delay:.1f}s before retry {attempt + 1}/5.", flush=True)
                time.sleep(delay)


def sync_dates(client, database_id, date_property):
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    explicit_start = os.getenv("SYNC_START_DATE")
    if explicit_start:
        start = date.fromisoformat(explicit_start)
    else:
        latest = client.databases.query(
            database_id=database_id,
            sorts=[{"property": date_property, "direction": "descending"}],
            page_size=1,
        )["results"]
        start = today - timedelta(days=30)
        if latest:
            value = latest[0]["properties"][date_property]["date"]
            if value:
                start = date.fromisoformat(value["start"][:10]) - timedelta(days=7)
    if start > today:
        raise ValueError("SYNC_START_DATE cannot be in the future")
    return [start + timedelta(days=i) for i in range((today - start).days + 1)]


def all_rows(client, database_id, **kwargs):
    rows = []
    while True:
        response = client.databases.query(database_id=database_id, **kwargs)
        rows.extend(response["results"])
        if not response.get("has_more"):
            return rows
        kwargs["start_cursor"] = response["next_cursor"]
