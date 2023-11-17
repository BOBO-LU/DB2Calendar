from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials from the JSON file
credentials = service_account.Credentials.from_service_account_file(
    "service_account_key.json", scopes=["https://www.googleapis.com/auth/drive"]
)

# Create a Google Drive API client
service = build("drive", "v3", credentials=credentials)

# Search for all Google Sheets files in Google Drive
results = (
    service.files()
    .list(
        q="mimeType='application/vnd.google-apps.spreadsheet'", fields="files(id, name)"
    )
    .execute()
)

# List the Google Sheets
print(service.files().list().execute())
for file in results.get("files", []):
    print(f"Name: {file['name']}, ID: {file['id']}")
