from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

service = build('calendar', 'v3', credentials=creds)

# Bulk create events
events_to_create = [
    {
        'summary': 'Meeting 1',
        'start': {'dateTime': '2024-07-26T10:00:00-07:00'},
        'end': {'dateTime': '2024-07-26T11:00:00-07:00'},
    },
    {
        'summary': 'Meeting 2', 
        'start': {'dateTime': '2024-07-26T14:00:00-07:00'},
        'end': {'dateTime': '2024-07-26T15:00:00-07:00'},
    }
]

for event in events_to_create:
    service.events().insert(calendarId='primary', body=event).execute()
    print(f"Created: {event['summary']}")
