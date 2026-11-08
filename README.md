[![Sync Garmin to Notion](https://github.com/chloevoyer/garmin-to-notion/actions/workflows/sync_garmin_to_notion.yml/badge.svg?branch=main)](https://github.com/chloevoyer/garmin-to-notion/actions/workflows/sync_garmin_to_notion.yml)
# Garmin to Notion Integration :watch:
This project connects your Garmin activities and personal records to your Notion database, allowing you to keep track of your performance metrics in one place.

## Features :sparkles:  
  🔄  Automatically sync Garmin activities to Notion in real-time  
  📊  Track detailed activity metrics (distance, pace, heart rate)  
  🎯  Extract and track personal records (fastest 1K, longest ride)  
  👣  Optional daily steps tracker
  😴  Optional sleep data tracker  
  🤖  Zero-touch automation once configured  
  📱  Compatible with all Garmin activities and devices  
  🔧  Easy setup with clear instructions and minimal coding required  

## Prerequisites :hammer_and_wrench:  
- A Notion account with API access.
- A Garmin Connect account to pull activity data.
- If you wish to sync your Peloton workouts with Garmin, see [peloton-to-garmin](https://github.com/philosowaffle/peloton-to-garmin)
## Getting Started :dart:
A detailed step-by-step guide is provided on my Notion template [here](https://chloevoyer.notion.site/Set-up-Guide-17915ce7058880559a3ac9f8a0720046).
For more advanced users, follow these steps to set up the integration:
### 1. Fork this GitHub Repository
### 2. Duplicate my [Notion Template](https://www.notion.so/templates/fitness-tracker-738)
* Save your Activities and Personal Records database ID (you will need it for step 4)
  * Optional: Daily Steps database ID
  * Look at the URL: notion.so/username/[string-of-characters]
  * The database ID is everything after your “username/“ and before the “?v”
### 3. Create Notion Token
* Go to [Notion Integrations](https://www.notion.so/profile/integrations).
* [Create](https://developers.notion.com/docs/create-a-notion-integration) a new integration and copy the integration token.
* [Share](https://www.notion.so/help/add-and-manage-connections-with-the-api#enterprise-connection-settings) the integration with the target database in Notion.
### 4. Set Environment Secrets
* Environment secrets to define:
  * GARMIN_EMAIL
  * GARMIN_PASSWORD
  * GARMINTOKENS (optional, the contents of the new Garmin client's `garmin_tokens.json` to reuse a saved session)
  * NOTION_TOKEN
  * NOTION_DB_ID
  * NOTION_PR_DB_ID
  * NOTION_STEPS_DB_ID (optional)
  * NOTION_SLEEP_DB_ID (optional)
### 5. Run Scripts (if not using automatic workflow)
Use Python 3.12 or later and install dependencies with `python -m pip install -r requirements.txt`.
The Garmin client now uses a different sign-in flow. If you have a saved session
from the older garth-based client, sign in again to create a new session.
For local runs, set `GARMINTOKENS=~/.garminconnect` to save and reuse the
session. To reuse it in GitHub Actions, add the JSON file contents as the
optional repository secret above. If the saved session stops working, replace
the secret with a fresh session.

* Run [garmin-activities.py](https://github.com/chloevoyer/garmin-to-notion/blob/main/garmin-activities.py) to sync your Garmin activities to Notion.  
`python garmin-activities.py`
* Run [person-records.py](https://github.com/chloevoyer/garmin-to-notion/blob/main/personal-records.py) to extract activity records (e.g., fastest run, longest ride).  
`python personal-records.py` 
## Example Configuration :pencil:  
You can customize the scripts to fit your needs by modifying environment variables and Notion database settings.  

Here is a screenshot of what my Notion dashboard looks like:  
![garmin-to-notion-template](https://github.com/user-attachments/assets/b37077cc-fe87-466f-9424-8ba9e4efa909)


My Notion template is available for free and can be duplicated to your Notion [here](https://www.notion.so/templates/fitness-tracker-738)

## Acknowledgements :raised_hands:  
- Reference dictionary and examples can be found in [cyberjunky/python-garminconnect](https://github.com/cyberjunky/python-garminconnect.git).
- This project was inspired by [n-kratz/garmin-notion](https://github.com/n-kratz/garmin-notion.git).
## Contributing :handshake:   
Contributions are welcome! If you find a bug or want to add a feature, feel free to open an issue or submit a pull request. Financial contributions are also greatly appreciated :blush:    

<a href="https://www.buymeacoffee.com/cvoyer" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>   

## :copyright: License  
This project is licensed under the MIT License. See the LICENSE file for more details.


## Full Fitness Tracker sync

The workflow runs all four datasets using one Garmin login and a shared,
rate-limited Notion client. Configure all four database secrets listed above.
It runs daily at 08:17 and 20:17 Asia/Shanghai, and can also be run manually.

Steps and sleep resume from seven days before the latest stored date through
today, updating existing days as well as filling missing ones. An empty database
starts with the last 30 days. To repair older gaps or existing sleep time labels,
enter a YYYY-MM-DD date in the manual workflow's start_date input. For this
tracker, use 2026-02-09 for the first historical repair run. Subsequent runs can
leave it empty. Sleep days without available sleep data are skipped.

Personal Records uses Garmin's current records, matches existing rows by typeId
and date, and corrects names and values including half marathon and marathon.
Previous/template rows for supported types are retained with PR unchecked once
the current records have been saved. Garmin records must already be accepted
in Garmin Connect; the script does not calculate new records from Activities.
