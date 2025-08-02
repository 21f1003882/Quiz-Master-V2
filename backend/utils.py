# backend/utils.py
from datetime import datetime

def parse_datetime(date_string):
    if not date_string:
        return None
    try:
        
        if isinstance(date_string, str) and date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
      
        return datetime.fromisoformat(date_string)
    except (ValueError, TypeError):
        try:
          
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            print(f"Warning: Could not parse datetime string: {date_string}")
            return None
    except Exception as e:
        print(f"Warning: Error parsing datetime string '{date_string}': {e}")
        return None
