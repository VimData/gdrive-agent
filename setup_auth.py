import os
import sys
# Add the current directory to path so we can import from gdrive_server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gdrive_server.drive_api import DriveAPI

def setup_auth():
    print("Starting Google Drive Authentication Setup...")
    print("This script will open your browser to log in to Google.")
    print("Ensure 'credentials.json' is in this directory.")
    
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found!")
        return

    try:
        # Initialize DriveAPI which triggers the auth flow
        drive = DriveAPI()
        print("\nAuthentication successful!")
        print("token.json has been created.")
        print("You can now run the agent.")
    except Exception as e:
        print(f"\nAuthentication failed: {e}")

if __name__ == "__main__":
    setup_auth()
