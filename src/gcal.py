#!/usr/bin/env python3

import argparse
import os.path
from create_google_cal.calendar_manager import CalendarManager
from create_google_cal.utils import parse_date

def main():
    parser = argparse.ArgumentParser(description='Manage Google Calendar events from CSV')
    parser.add_argument('-f', '--file', help='CSV file to import events from')
    parser.add_argument('-s', '--start', help='Start date for deletion (e.g., 28-7-2025)')
    parser.add_argument('-e', '--end', help='End date for deletion (e.g., 1-8-2025)')
    parser.add_argument('--delete', action='store_true', help='Delete events in date range')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    calendar_manager = CalendarManager()
    
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
                
            calendar_manager.delete_events_in_range(start_date, end_date, force=args.force)
            
        except ValueError as e:
            print(f"Error parsing dates: {e}")
            return
    
    elif args.file:
        # Check if file exists - handle both absolute and relative paths
        file_path = args.file
        if not os.path.isabs(file_path):
            # If relative path, check in data directory (go up one level from src)
            data_file_path = os.path.join('..', 'data', file_path)
            if os.path.exists(data_file_path):
                file_path = data_file_path
            elif not os.path.exists(file_path):
                print(f"Error: File {args.file} not found")
                return
        
        calendar_manager.create_events_from_csv(file_path)
    
    else:
        print("Usage examples:")
        print("  Create events from CSV: python gcal.py -f july28.csv")
        print("  Delete events in range: python gcal.py --delete -s 28-7-2025 -e 1-8-2025")
        print("  Delete events without confirmation: python gcal.py --delete -s 28-7-2025 -e 1-8-2025 --force")

if __name__ == "__main__":
    main()