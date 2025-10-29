"""
This is a MCP client for Google Calendar.

It uses the Google API Python Client and handles the OAuth 2.0 flow
to get permissions to access a user's calendar.

**SETUP REQUIRED:**
1.  Go to the Google Cloud Console: https://console.cloud.google.com/
2.  Create a new project.
3.  Go to "APIs & Services" > "Enabled APIs & services".
4.  Click "+ ENABLE APIS AND SERVICES" and enable the "Google Calendar API".
5.  Go to "APIs & Services" > "OAuth consent screen".
    -   Choose "External" and create an app.
    -   Give it a name (e.g., "FastAPI AI Agent").
    -   Enter your user support email.
    -   Add `.../auth/calendar` and `.../auth/calendar.events` to the scopes.
    -   Add your email address as a "Test user".
6.  Go to "APIs & Services" > "Credentials".
    -   Click "+ CREATE CREDENTIALS" > "OAuth client ID".
    -   Select "Desktop app" for the application type.
    -   Give it a name (e.g., "FastAPI Client").
    -   Click "Create".
    -   A window will pop up. Click "DOWNLOAD JSON".
7.  **Rename the downloaded file to `credentials.json` and place it in the
    same directory as this file (the `mcp_clients` folder).**

**FIRST RUN:**
When you first run the server and make an API request that needs the
calendar, the server will print a URL to the console. You MUST
copy/paste this URL into your browser, log in, and grant permission.
It will then save a `token.json` file for future use.
"""
import datetime
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scopes. If you modify these, delete token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Define file paths
# __file__ is the current file's path
BASE_DIR = os.getcwd()
CREDS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')


def get_calendar_service():
    """
    Handles the OAuth 2.0 flow and returns a Google Calendar service object.
    
    - Checks for an existing, valid `token.json`.
    - If not found or expired, it uses `credentials.json` to run the
      console-based auth flow.
    - Saves the new token for next time.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("  [GCal] Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                print(f"  [GCal] Error refreshing token: {e}")
                print("  [GCal] Token refresh failed. Please re-authorize.")
                creds = run_auth_flow()
        else:
            print("  [GCal] No valid token found. Starting auth flow...")
            creds = run_auth_flow()
        
        # Save the credentials for the next run
        print(f"  [GCal] Saving new token to {TOKEN_PATH}")
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    # Build and return the service object
    try:
        service = build('calendar', 'v3', credentials=creds)
        print("  [GCal] Google Calendar service created successfully.")
        return service
    except HttpError as error:
        print(f'  [GCal] An error occurred building the service: {error}')
        return None

def run_auth_flow():
    """Runs the console-based OAuth flow."""
    if not os.path.exists(CREDS_PATH):
        print(f"  [GCal] ERROR: `credentials.json` not found.")
        print(f"  [GCal] Please download it from Google Cloud Console and place it in {BASE_DIR}")
        raise FileNotFoundError(f"Missing {CREDS_PATH}. See instructions in google_calendar.py.")
        
    # Run the flow using the downloaded credentials
    # This will print a URL to the console for the user to visit
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def fetch_calendar_events(date: str) -> list[dict]:
    """
    REAL: Fetches Google Calendar events for a specific date.
    """
    print(f"  [REAL GCal] Fetching events for {date}")
    service = get_calendar_service()
    if not service:
        return {"error": "Failed to authenticate with Google Calendar."}

    try:
        # Parse the date and set up timezone-aware start/end times
        # This is crucial for Google API
        target_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        
        # We'll use the system's local timezone.
        # For a production server, you might want to specify one (e.g., 'UTC')
        local_tz = pytz.timezone('UTC') # Or get from user settings
        
        time_min = datetime.datetime.combine(target_date, datetime.time.min, tzinfo=local_tz)
        time_max = datetime.datetime.combine(target_date, datetime.time.max, tzinfo=local_tz)

        # Convert to ISO format
        time_min_iso = time_min.isoformat()
        time_max_iso = time_max.isoformat()

        print(f"  [REAL GCal] Querying from {time_min_iso} to {time_max_iso}")

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min_iso,
            timeMax=time_max_iso,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            print("  [REAL GCal] No events found.")
            return []

        # Simplify the event list to send back to the AI
        simplified_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            simplified_events.append({
                'summary': event['summary'],
                'start': start,
                'end': end,
                'id': event['id']
            })
        
        print(f"  [REAL GCal] Found {len(simplified_events)} events.")
        return simplified_events

    except HttpError as error:
        print(f'  [REAL GCal] An error occurred: {error}')
        return {'error': str(error)}
    except Exception as e:
        print(f'  [REAL GCal] A general error occurred: {e}')
        return {'error': str(e)}


def add_calendar_event(summary: str, date: str, start_time: str, end_time: str) -> dict:
    """
    REAL: Adds a new event to the Google Calendar.
    """
    print(f"  [REAL GCal] Adding event: '{summary}' on {date} from {start_time} to {end_time}")
    service = get_calendar_service()
    if not service:
        return {"error": "Failed to authenticate with Google Calendar."}

    try:
        # Construct the event body
        # We need to combine date and time and make it timezone-aware
        local_tz = pytz.timezone('Asia/Kolkata') # IST timezone
        
        start_dt = datetime.datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
        end_dt = datetime.datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')

        start_dt_tz = local_tz.localize(start_dt)
        end_dt_tz = local_tz.localize(end_dt)

        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_dt_tz.isoformat(),
                'timeZone': str(local_tz),
            },
            'end': {
                'dateTime': end_dt_tz.isoformat(),
                'timeZone': str(local_tz),
            },
            # You could also add attendees, location, etc.
            # 'attendees': [
            #     {'email': 'example@example.com'},
            # ],
        }

        print(f"  [REAL GCal] Inserting event: {event_body}")
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()

        print(f"  [REAL GCal] Event created successfully. Event ID: {created_event.get('id')}")
        
        # Return a simplified version for the AI
        return {
            'status': created_event.get('status'),
            'summary': created_event.get('summary'),
            'start': created_event['start'].get('dateTime'),
            'end': created_event['end'].get('dateTime'),
            'id': created_event.get('id'),
            'htmlLink': created_event.get('htmlLink')
        }

    except HttpError as error:
        print(f'  [REAL GCal] An error occurred: {error}')
        return {'error': str(error)}
    except Exception as e:
        print(f'  [REAL GCal] A general error occurred: {e}')
        return {'error': str(e)}

