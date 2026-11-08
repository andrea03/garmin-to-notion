"""Run all configured Fitness Tracker syncs with one Garmin session."""
import os
import runpy
from pathlib import Path

from dotenv import load_dotenv
from garminconnect import Garmin
from sync_common import RateLimitedNotionClient


def main():
    load_dotenv()
    required = ("GARMIN_EMAIL", "GARMIN_PASSWORD", "NOTION_TOKEN", "NOTION_DB_ID",
                "NOTION_STEPS_DB_ID", "NOTION_SLEEP_DB_ID", "NOTION_PR_DB_ID")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise SystemExit("Missing configuration: " + ", ".join(missing))
    garmin = Garmin(os.environ["GARMIN_EMAIL"], os.environ["GARMIN_PASSWORD"])
    garmin.login()
    failures = []
    with RateLimitedNotionClient(auth=os.environ["NOTION_TOKEN"]) as notion:
        for script in ("garmin-activities.py", "daily-steps.py", "sleep-data.py", "personal-records.py"):
            print(f"Starting {script}", flush=True)
            try:
                runpy.run_path(str(Path(__file__).with_name(script)))["main"](garmin, notion)
            except Exception as error:
                print(f"{script} failed ({type(error).__name__}).", flush=True)
                failures.append(script)
    if failures:
        raise SystemExit("Failed syncs: " + ", ".join(failures))


if __name__ == "__main__":
    main()
