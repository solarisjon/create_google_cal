# Google Calendar CSV Manager

A Python tool for managing Google Calendar events from CSV files. Create events in bulk or delete events within a date range.

## Features

- **Import Events**: Create multiple calendar events from a CSV file
- **Delete Events**: Remove all events within a specified date range
- **Flexible Date Formats**: Supports various date formats (DD-MM-YYYY, MM/DD/YYYY, etc.)
- **Interactive Confirmation**: Optional confirmation prompts for deletion operations
- **Modular Architecture**: Clean separation of concerns with dedicated modules

## Project Structure

```
create_google_cal/
├── src/
│   ├── gcal.py                     # Main entry point
│   └── create_google_cal/          # Core modules
│       ├── __init__.py
│       ├── auth.py                 # Google OAuth authentication
│       ├── calendar_manager.py     # Calendar operations
│       ├── main.py                 # CLI interface (legacy)
│       └── utils.py                # Date parsing utilities
├── config/                         # Google API credentials (gitignored)
│   ├── credentials.json            # OAuth client secrets
│   └── token.json                  # Access tokens (auto-generated)
├── data/                           # CSV data files (gitignored)
│   └── *.csv                       # Event data files
├── archive/                        # Old versions
├── tests/                          # Test files
├── docs/                           # Documentation
├── pyproject.toml                  # Project configuration
├── uv.lock                         # Dependency lock file
└── README.md                       # This file
```

## Setup

### Prerequisites

- Python 3.10+
- UV package manager
- Google Cloud Project with Calendar API enabled

### 1. Google API Setup

#### Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** dropdown at the top
3. Click **"New Project"**
4. Enter a project name (e.g., "Calendar Manager")
5. Click **"Create"**
6. Make sure your new project is selected

#### Step 2: Enable the Google Calendar API

1. In the Google Cloud Console, go to **APIs & Services > Library**
2. Search for "Google Calendar API"
3. Click on **"Google Calendar API"**
4. Click **"Enable"**
5. Wait for the API to be enabled (this may take a moment)

#### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Choose **"External"** user type (unless you have a Google Workspace account)
3. Click **"Create"**
4. Fill in the required fields:
   - **App name**: "Calendar Manager" (or your preferred name)
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
5. Click **"Save and Continue"**
6. On the "Scopes" page, click **"Save and Continue"** (no changes needed)
7. On the "Test users" page, add your email address by clicking **"Add Users"**
8. Click **"Save and Continue"**
9. Review and click **"Back to Dashboard"**

#### Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **"Create Credentials"** > **"OAuth client ID"**
3. Choose **"Desktop application"** as the application type
4. Enter a name: "Calendar Manager Client"
5. Click **"Create"**
6. A dialog will show your credentials - click **"Download JSON"**
7. Save the downloaded file (it will have a long name like `client_secret_xxxxx.json`)

#### Step 5: Set Up Credentials File

1. Create a `config/` directory in your project root if it doesn't exist:
   ```bash
   mkdir -p config
   ```
2. Rename the downloaded file to `credentials.json` and place it in the `config/` directory:
   ```bash
   mv ~/Downloads/client_secret_*.json config/credentials.json
   ```
3. Verify the file structure:
   ```
   create_google_cal/
   ├── config/
   │   └── credentials.json    # Your OAuth credentials
   └── src/
       └── gcal.py
   ```

#### Important Security Notes

- ⚠️ **Never commit `credentials.json` to version control**
- The file contains sensitive client secrets
- Keep it in the `config/` directory (already in `.gitignore`)
- Don't share this file publicly or via email

### 2. Install Dependencies

```bash
# Clone or download the project
cd create_google_cal

# Install dependencies with UV
uv sync
```

### 3. Configure Credentials

1. Create a `config/` directory in the project root
2. Place your downloaded credentials file as `config/credentials.json`
3. The app will create `config/token.json` automatically on first run

## Usage

### Running the Application

Navigate to the `src/` directory and use UV to run the application:

```bash
cd src
uv run python gcal.py [options]
```

### First Time Setup

Before using the application for the first time, run the setup command to verify your credentials:

```bash
cd src
uv run python gcal.py --setup
```

This will:
- Display setup instructions if credentials are missing
- Validate your `credentials.json` file structure
- Confirm you're ready to use the application

### Import Events from CSV

```bash
# Import events from a CSV file
uv run python gcal.py -f july28.csv
```

#### CSV Format

Your CSV file should have the following columns:
- `date`: Event date (supports various formats: DD-MM-YYYY, MM/DD/YYYY, YYYY-MM-DD)
- `start time`: Start time (HH:MM, HH:MM AM/PM)
- `end time`: End time (HH:MM, HH:MM AM/PM)
- `event name`: Event title/summary

Example CSV:
```csv
date,start time,end time,event name
28/07/2025,09:00,10:30,Team Meeting
29/07/2025,14:00,15:00,Project Review
30/07/2025,11:00 AM,12:00 PM,Client Call
```

### Delete Events in Date Range

```bash
# Delete events with confirmation prompt
uv run python gcal.py --delete -s 28-7-2025 -e 1-8-2025

# Delete events without confirmation (force)
uv run python gcal.py --delete -s 28-7-2025 -e 1-8-2025 --force
```

### Command Line Options

```
usage: gcal.py [-h] [-f FILE] [-s START] [-e END] [--delete] [--force] [--setup]

Manage Google Calendar events from CSV

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  CSV file to import events from
  -s START, --start START
                        Start date for deletion (e.g., 28-7-2025)
  -e END, --end END     End date for deletion (e.g., 1-8-2025)
  --delete              Delete events in date range
  --force               Skip confirmation prompt
  --setup               Show Google API setup instructions
```

## Configuration

### Timezone

By default, events are created with `America/Los_Angeles` timezone. To change this:

1. Edit `src/create_google_cal/calendar_manager.py`
2. Modify the `timeZone` field in the `create_events_from_csv` method

### File Paths

- CSV files are automatically searched in the `../data/` directory when using relative paths
- Config files are expected in the `../config/` directory
- All paths are relative to the `src/` directory

## Development

### Project Architecture

The project uses a modular architecture:

- **gcal.py**: Single entry point that imports from core modules
- **auth.py**: Handles Google OAuth authentication and token management
- **calendar_manager.py**: Contains the `CalendarManager` class with calendar operations
- **utils.py**: Date parsing utilities supporting multiple formats
- **main.py**: Legacy CLI interface (kept for compatibility)

### Adding Features

1. Authentication logic → `auth.py`
2. Calendar operations → `calendar_manager.py`
3. Date/time utilities → `utils.py`
4. CLI interface → `gcal.py`

## Security

- Credentials and tokens are stored in the `config/` directory
- The `config/` and `data/` directories are excluded from version control
- Never commit `credentials.json` or `token.json` files

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'create_google_cal'"**
   - Make sure you're running from the `src/` directory
   - Check that all `__init__.py` files exist

2. **"Credentials file not found"**
   - Ensure `config/credentials.json` exists and is valid JSON
   - Verify the file path is correct relative to the `src/` directory

3. **"Invalid control character" JSON errors**
   - Clean up your credentials.json file - remove any extra spaces or control characters
   - Ensure the JSON is properly formatted

4. **"File not found" for CSV**
   - Place CSV files in the `data/` directory
   - Use the filename without path: `gcal.py -f myfile.csv`

## License

This project is for personal/educational use. Ensure compliance with Google Calendar API terms of service.