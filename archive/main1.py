import csv
from datetime import datetime, timedelta
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

def parse_datetime(date_str, time_str):
    """Convert date and time strings to datetime object"""
    # Try different date formats
    date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y']
    time_formats = ['%H:%M', '%I:%M %p', '%H:%M:%S', '%I:%M:%S %p']
    
    parsed_date = None
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), date_format).date()
            break
        except ValueError:
            continue
    
    if not parsed_date:
        raise ValueError(f"Could not parse date: {date_str}")
    
    parsed_time = None
    for time_format in time_formats:
        try:
            parsed_time = datetime.strptime(time_str.strip(), time_format).time()
            break
        except ValueError:
            continue
    
    if not parsed_time:
        raise ValueError(f"Could not parse time: {time_str}")
    
    return datetime.combine(parsed_date, parsed_time)

def create_events_from_csv(filename):
    # Get credentials and build service
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    events_created = 0
    
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                # Parse the CSV data
                date = row['date'].strip()
                start_time = row['start time'].strip()
                end_time = row['end time'].strip()
                event_name = row['event name'].strip()
                
                # Convert to datetime objects
                start_datetime = parse_datetime(date, start_time)
                end_datetime = parse_datetime(date, end_time)
                
                # Create the event
                event = {
                    'summary': event_name,
                    'start': {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'America/Los_Angeles',  # Change to your timezone
                    },
                    'end': {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'America/Los_Angeles',  # Change to your timezone
                    },
                }
                
                # Insert the event
                created_event = service.events().insert(calendarId='primary', body=event).execute()
                print(f"Created: {event_name} on {date} from {start_time} to {end_time}")
                events_created += 1
                
            except Exception as e:
                print(f"Error creating event for row {row}: {e}")
                continue
    
    print(f"\nTotal events created: {events_created}")

if __name__ == "__main__":
    create_events_from_csv('july28.csv')
