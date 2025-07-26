import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']

def validate_credentials_file(credentials_path):
    """Validate that the credentials file exists and has the correct structure"""
    if not os.path.exists(credentials_path):
        return False, f"Credentials file not found at {credentials_path}"
    
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        # Check for required structure
        if 'installed' not in creds_data:
            return False, "Invalid credentials file: missing 'installed' section"
        
        installed = creds_data['installed']
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        
        for field in required_fields:
            if field not in installed:
                return False, f"Invalid credentials file: missing '{field}' field"
        
        return True, "Credentials file is valid"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in credentials file: {e}"
    except Exception as e:
        return False, f"Error reading credentials file: {e}"

def setup_credentials_help():
    """Display helpful setup instructions"""
    print("\n" + "="*60)
    print("🔑 GOOGLE CALENDAR API SETUP REQUIRED")
    print("="*60)
    print("\nTo use this application, you need to set up Google Calendar API access:")
    print("\n1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Calendar API")
    print("4. Create OAuth 2.0 credentials for 'Desktop application'")
    print("5. Download the credentials JSON file")
    print("6. Save it as: config/credentials.json")
    print("\n📖 For detailed instructions, see the README.md file")
    print("\n⚠️  Make sure the credentials file is in the config/ directory:")
    print("   create_google_cal/")
    print("   ├── config/")
    print("   │   └── credentials.json  ← Your OAuth credentials here")
    print("   └── src/")
    print("       └── gcal.py")
    print("\n" + "="*60)

def get_credentials():
    """Get valid Google API credentials"""
    creds = None
    
    # Check if token.json exists (saved credentials)
    token_path = os.path.join('..', 'config', 'token.json')
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Warning: Could not load existing token ({e}). Will create new one.")
            # Remove corrupted token file
            os.remove(token_path)
            creds = None
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Warning: Could not refresh token ({e}). Will create new one.")
                creds = None
        
        if not creds:
            credentials_path = os.path.join('..', 'config', 'credentials.json')
            
            # Validate credentials file before proceeding
            is_valid, message = validate_credentials_file(credentials_path)
            if not is_valid:
                setup_credentials_help()
                raise FileNotFoundError(f"\n❌ {message}\n\nPlease follow the setup instructions above.")
            
            print("✅ Valid credentials file found")
            print("🌐 Opening browser for Google OAuth authorization...")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ Authorization successful!")
            except Exception as e:
                print(f"❌ Authorization failed: {e}")
                print("\n💡 Troubleshooting tips:")
                print("   - Make sure you're signed into the correct Google account")
                print("   - Check that the Calendar API is enabled in Google Cloud Console")
                print("   - Verify your email is added as a test user in OAuth consent screen")
                raise
        
        # Save credentials for next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds