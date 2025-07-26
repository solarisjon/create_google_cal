from datetime import datetime

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