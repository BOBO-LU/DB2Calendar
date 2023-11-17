from __future__ import print_function

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def search_file():
    # Load credentials from the JSON file
    credentials = service_account.Credentials.from_service_account_file(
        "service_account_key.json", scopes=["https://www.googleapis.com/auth/drive"]
    )

    try:
        # create drive api client
        service = build("drive", "v3", credentials=credentials)
        files = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = (
                service.files()
                .list(
                    q="mimeType != 'application/vnd.google-apps.folder'",
                    spaces="drive",
                    fields="nextPageToken, " "files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                # Process change
                print(f'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

    return files


if __name__ == "__main__":
    search_file()
