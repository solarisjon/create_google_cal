import csv
import argparse
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

def parse_date(date_str):
    """Parse date string in various formats"""
    date_formats = ['%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str.strip(), date_format).date()
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")

def parse_datetime(date_str, time_str):
    """Convert date and time strings to datetime object"""
    # Try different date formats
    date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y']
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

def delete_events_in_range(start_date, end_date):
    """Delete all events in the specified date range"""
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    # Convert dates to RFC3339 format for API
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    start_rfc = start_datetime.isoformat() + 'Z'
    end_rfc = end_datetime.isoformat() + 'Z'
    
    print(f"Searching for events between {start_date} and {end_date}...")
    
    # Get events in the date range
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_rfc,
        timeMax=end_rfc,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        print("No events found in the specified date range.")
        return 0
    
    print(f"Found {len(events)} events to delete:")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"  - {event.get('summary', 'No title')} ({start})")
    
    # Ask for confirmation
    confirm = input(f"\nAre you sure you want to delete these {len(events)} events? (y/N): ")
    if confirm.lower() not in ['y', 'yes']:
        print("Deletion cancelled.")
        return 0
    
    # Delete events
    deleted_count = 0
    for event in events:
        try:
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
            print(f"Deleted: {event.get('summary', 'No title')}")
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting event {event.get('summary', 'No title')}: {e}")
    
    print(f"\nTotal events deleted: {deleted_count}")
    return deleted_count

def create_events_from_csv(filename):
    """Create events from CSV file"""
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

def main():
    parser = argparse.ArgumentParser(description='Manage Google Calendar events from CSV')
    parser.add_argument('-f', '--file', help='CSV file to import events from')
    parser.add_argument('-s', '--start', help='Start date for deletion (e.g., 28-7-2025)')
    parser.add_argument('-e', '--end', help='End date for deletion (e.g., 1-8-2025)')
    parser.add_argument('--delete', action='store_true', help='Delete events in date range')
    
    args = parser.parse_args()
    
    if args.delete:
        if not args.start or not args.end:
            print("Error: --delete requires both --start and --end dates")
            return
        
        try:
            start_date = parse_date(args.start)
            end_date = parse_date(args.end)
            
            if start_date > end_date:
                print("Error: Start date must be before end date")
                return
                
            delete_events_in_range(start_date, end_date)
            
        except ValueError as e:
            print(f"Error parsing dates: {e}")
            return
    
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found")
            return
        
        create_events_from_csv(args.file)
    
    else:
        print("Usage examples:")
        print("  Create events from CSV: python gcreate.py -f july28.csv")
        print("  Delete events in range: python gcreate.py --delete -s 28-7-2025 -e 1-8-2025")

if __name__ == "__main__":
    main()
