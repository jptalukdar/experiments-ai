"""
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
def run_google_setup():
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


if __name__ == "__main__":
    run_google_setup()