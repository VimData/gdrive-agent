import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveAPI:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticates the user and creates the Drive service."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}. Please download it from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=8080)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def create_folder(self, name, parent_id=None):
        """Creates a folder in Google Drive."""
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def find_folder(self, name, parent_id=None):
        """Finds a folder by name and parent ID."""
        query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = self.service.files().list(
            q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if not items:
            return None
        return items[0]['id']

    def ensure_folder_structure(self, year, month, media_type="images"):
        """Ensures the /year/month/media_type folder structure exists."""
        # Normalize media type
        media_type = media_type.lower() if media_type else "images"
        if media_type not in ["images", "videos"]:
            media_type = "images"
        
        # Check/Create Year Folder
        year_id = self.find_folder(str(year))
        if not year_id:
            year_id = self.create_folder(str(year))
        
        # Check/Create Month Folder inside Year
        month_id = self.find_folder(str(month), parent_id=year_id)
        if not month_id:
            month_id = self.create_folder(str(month), parent_id=year_id)
        
        # Check/Create Media Type Folder inside Month
        media_id = self.find_folder(media_type, parent_id=month_id)
        if not media_id:
            media_id = self.create_folder(media_type, parent_id=month_id)
            
        return media_id

    def upload_file(self, file_path, folder_id):
        """Uploads a file to the specified folder."""
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

if __name__ == '__main__':
    # Test run
    try:
        drive = DriveAPI()
        print("Authentication successful.")
    except Exception as e:
        print(f"Error: {e}")
