import csv
import os
from datetime import datetime
from googleapiclient.discovery import build
from .auth import get_credentials
from .utils import parse_datetime

class CalendarManager:
    def __init__(self):
        self.creds = get_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def delete_events_in_range(self, start_date, end_date, force=False):
        """Delete all events in the specified date range"""
        # Convert dates to RFC3339 format for API
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        start_rfc = start_datetime.isoformat() + 'Z'
        end_rfc = end_datetime.isoformat() + 'Z'
        
        print(f"Searching for events between {start_date} and {end_date}...")
        
        # Get events in the date range
        events_result = self.service.events().list(
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
        
        # Ask for confirmation unless force flag is used
        if not force:
            confirm = input(f"\nAre you sure you want to delete these {len(events)} events? (y/N): ")
            if confirm.lower() not in ['y', 'yes']:
                print("Deletion cancelled.")
                return 0
        
        # Delete events
        deleted_count = 0
        for event in events:
            try:
                self.service.events().delete(calendarId='primary', eventId=event['id']).execute()
                print(f"Deleted: {event.get('summary', 'No title')}")
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting event {event.get('summary', 'No title')}: {e}")
        
        print(f"\nTotal events deleted: {deleted_count}")
        return deleted_count
    
    def create_events_from_csv(self, filename):
        """Create events from CSV file"""
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
                    created_event = self.service.events().insert(calendarId='primary', body=event).execute()
                    print(f"Created: {event_name} on {date} from {start_time} to {end_time}")
                    events_created += 1
                    
                except Exception as e:
                    print(f"Error creating event for row {row}: {e}")
                    continue
        
        print(f"\nTotal events created: {events_created}")
        return events_created