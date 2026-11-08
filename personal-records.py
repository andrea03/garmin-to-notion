from datetime import datetime, UTC
from dotenv import load_dotenv
from garminconnect import Garmin
from sync_common import RateLimitedNotionClient as Client, sync_dates, all_rows
import os

def get_icon_for_record(activity_name):
    icon_map = {
        "1K": "🥇",
        "1mi": "⚡",
        "5K": "👟",
        "10K": "⭐",
        "Longest Run": "🏃",
        "Longest Ride": "🚴",
        "Total Ascent": "🚵",
        "Max Avg Power (20 min)": "🔋",
        "Most Steps in a Day": "👣",
        "Most Steps in a Week": "🚶",
        "Most Steps in a Month": "📅",
        "Longest Goal Streak": "✔️",
        "Other": "🏅"
    }
    return icon_map.get(activity_name, "🏅")  # Default to "Other" icon if not found

def get_cover_for_record(activity_name):
    cover_map = {
        "1K": "https://images.unsplash.com/photo-1526676537331-7747bf8278fc?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "1mi": "https://images.unsplash.com/photo-1638183395699-2c0db5b6afbb?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "5K": "https://images.unsplash.com/photo-1571008887538-b36bb32f4571?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "10K": "https://images.unsplash.com/photo-1529339944280-1a37d3d6fa8c?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Longest Run": "https://images.unsplash.com/photo-1532383282788-19b341e3c422?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Longest Ride": "https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Max Avg Power (20 min)": "https://images.unsplash.com/photo-1591741535018-d042766c62eb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2MzkyMXwwfDF8c2VhcmNofDJ8fHNwaW5uaW5nfGVufDB8fHx8MTcyNjM1Mzc0Mnww&ixlib=rb-4.0.3&q=80&w=4800",
        "Most Steps in a Day": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Most Steps in a Week": "https://images.unsplash.com/photo-1602174865963-9159ed37e8f1?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Most Steps in a Month": "https://images.unsplash.com/photo-1580058572462-98e2c0e0e2f0?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Longest Goal Streak": "https://images.unsplash.com/photo-1477332552946-cfb384aeaf1c?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800"
    }
    return cover_map.get(activity_name, "https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800") 

def format_activity_type(activity_type):
    if activity_type is None:
        return "Walking"
    return activity_type.replace('_', ' ').title()

def format_activity_name(activity_name):
    if not activity_name or activity_name is None:
        return "Unnamed Activity"
    return activity_name

def format_garmin_value(value, activity_type, typeId):
    if typeId in (5, 6):
        distance = 21.0975 if typeId == 5 else 42.195
        seconds = round(value)
        pace_seconds = round(value / distance)
        return (
            f"{seconds // 3600}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}",
            f"{pace_seconds // 60}:{pace_seconds % 60:02d} /km",
        )
    if typeId  == 1:  # 1K
        total_seconds = round(value)  # Round to the nearest second
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        formatted_value = f"{minutes}:{seconds:02d} /km"
        pace = formatted_value  # For these types, the value is the pace
        return formatted_value, pace

    if typeId  == 2:  # 1mile
        total_seconds = round(value)  # Round to the nearest second
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        formatted_value = f"{minutes}:{seconds:02d}"
        total_pseconds = total_seconds / 1.60934  # Divide by 1.60934 to get pace per km
        pminutes = int(total_pseconds // 60)      # Convert to integer
        pseconds = int(total_pseconds % 60)       # Convert to integer
        formatted_pace = f"{pminutes}:{pseconds:02d} /km"
        return formatted_value, formatted_pace

    if typeId == 3:  # 5K
        total_seconds = round(value) 
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        formatted_value = f"{minutes}:{seconds:02d}"
        total_pseconds = total_seconds // 5  # Divide by 5km
        pminutes = total_pseconds // 60
        pseconds = total_pseconds % 60
        formatted_pace = f"{pminutes}:{pseconds:02d} /km"
        return formatted_value, formatted_pace

    if typeId == 4:  # 10K
        # Round to the nearest second
        total_seconds = round(value)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            formatted_value = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            formatted_value = f"{minutes}:{seconds:02d}"
        total_pseconds = total_seconds // 10  # Divide by 10km
        phours = total_pseconds // 3600
        pminutes = (total_pseconds % 3600) // 60
        pseconds = total_pseconds % 60
        formatted_pace = f"{pminutes}:{pseconds:02d} /km"
        return formatted_value, formatted_pace

    if typeId in [7, 8]:  # Longest Run, Longest Ride
        value_km = value / 1000
        formatted_value = f"{value_km:.2f} km"
        pace = ""  # No pace for these types
        return formatted_value, pace

    if typeId == 9:  # Total Ascent
        value_m = int(value)
        formatted_value = f"{value_m:,} m"
        pace = ""
        return formatted_value, pace

    if typeId == 10:  # Max Avg Power
        value_w = round(value)
        formatted_value = f"{value_w} W"
        pace = ""
        return formatted_value, pace

    if typeId in [12, 13, 14]:  # Step counts
        value_steps = round(value)
        formatted_value = f"{value_steps:,}"
        pace = ""
        return formatted_value, pace

    if typeId == 15:  # Longest Goal Streak
        value_days = round(value)
        formatted_value = f"{value_days} days"
        pace = ""
        return formatted_value, pace

    # Default case
    if int(value // 60) < 60:  # If total time is less than an hour
        minutes = int(value // 60)
        seconds = round((value / 60 - minutes) * 60, 2)
        formatted_value = f"{minutes}:{seconds:05.2f}"
    else:  # If total time is one hour or more
        hours = int(value // 3600)
        minutes = int((value % 3600) // 60)
        seconds = round(value % 60, 2)
        formatted_value = f"{hours}:{minutes:02}:{seconds:05.2f}"
    
    pace = ""
    return formatted_value, pace

def replace_activity_name_by_typeId(typeId):
    typeId_name_map = {
        1: "1K",
        2: "1mi",
        3: "5K",
        4: "10K",
        5: "Half Marathon",
        6: "Marathon",
        7: "Longest Run",
        8: "Longest Ride",
        9: "Total Ascent",
        10: "Max Avg Power (20 min)",
        12: "Most Steps in a Day",
        13: "Most Steps in a Week",
        14: "Most Steps in a Month",
        15: "Longest Goal Streak"
    }
    return typeId_name_map.get(typeId, "Unnamed Activity")


def record_time(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).replace(second=0, microsecond=0)


def main(garmin=None, client=None):
    load_dotenv()
    database_id = os.environ["NOTION_PR_DB_ID"]
    if garmin is None:
        garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
        garmin.login()
    if client is None:
        client = Client(auth=os.environ["NOTION_TOKEN"])

    records = garmin.get_personal_record(include_history=False)
    if not isinstance(records, list) or not records:
        raise ValueError("Garmin returned no usable personal records; existing records were preserved")
    # Validate the whole response before changing current-record flags.
    current = {}
    for record in records:
        type_id = record["typeId"]
        if type_id == 16:
            continue
        name = replace_activity_name_by_typeId(type_id)
        if name == "Unnamed Activity":
            raise ValueError(f"Unsupported Garmin personal record type: {type_id}")
        if type_id in current:
            raise ValueError(f"Multiple current Garmin records for type {type_id}")
        record_time(record["prStartTimeGmtFormatted"])
        value, pace = format_garmin_value(record["value"], record.get("activityType"), type_id)
        current[type_id] = (record, name, value, pace)

    rows = all_rows(client, database_id)
    selected_ids = set()
    for type_id, (record, name, value, pace) in current.items():
        timestamp = record_time(record["prStartTimeGmtFormatted"])
        match = None
        for row in rows:
            props = row["properties"]
            old_date = props["Date"].get("date")
            if props["typeId"]["number"] == type_id and old_date and record_time(old_date["start"]) == timestamp:
                match = row
                break
        properties = {
            "Date": {"date": {"start": timestamp.isoformat()}},
            "Record": {"title": [{"text": {"content": name}}]},
            "Activity Type": {"select": {"name": format_activity_type(record.get("activityType"))}},
            "typeId": {"number": type_id},
            "Value": {"rich_text": [{"text": {"content": value}}]},
            "Pace": {"rich_text": [{"text": {"content": pace}}]} if pace else {"rich_text": []},
            "PR": {"checkbox": True},
        }
        if match:
            saved = client.pages.update(page_id=match["id"], properties=properties)
        else:
            saved = client.pages.create(parent={"database_id": database_id}, properties=properties,
                                        icon={"emoji": get_icon_for_record(name)})
        selected_ids.add(saved["id"])

    # Mark historical/template rows as non-current only after all current records
    # have been saved. A failed run can safely resume on the next invocation.
    for row in rows:
        props = row["properties"]
        if row["id"] not in selected_ids and props["PR"]["checkbox"]:
            type_id = props["typeId"]["number"]
            if replace_activity_name_by_typeId(type_id) != "Unnamed Activity":
                client.pages.update(page_id=row["id"], properties={"PR": {"checkbox": False}})
    print(f"Synced {len(current)} current personal records.", flush=True)


if __name__ == '__main__':
    main()
