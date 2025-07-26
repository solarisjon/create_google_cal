from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    
    # Check if token.json exists (saved credentials)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# Get credentials first
creds = get_credentials()

# Now build the service
service = build('calendar', 'v3', credentials=creds)

# Create an event
event = {
    'summary': 'Test Event',
    'start': {
        'dateTime': '2025-07-25T10:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2025-07-25T11:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
}

event = service.events().insert(calendarId='primary', body=event).execute()
print(f'Event created: {event.get("htmlLink")}')
