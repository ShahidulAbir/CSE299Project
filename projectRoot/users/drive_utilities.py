from __future__ import print_function

import io
import os.path
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


# def create_folder():
#     creds = main()
#
#     try:
#         # create drive api client
#         service = build('drive', 'v3', credentials=creds)
#         file_metadata = {
#             'name': 'Invoices',
#             'mimeType': 'application/vnd.google-apps.folder'
#         }
#
#         # pylint: disable=maybe-no-member
#         file = service.files().create(body=file_metadata, fields='id'
#                                       ).execute()
#         print(F'Folder ID: "{file.get("id")}".')
#         return file.get('id')
#
#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         return None


def download_file(real_file_id):
    creds = main()

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.getvalue()


def list_files():
    creds = main()

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        files = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            query = f"mimeType != 'application/vnd.google-apps.folder'"
            response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                if file.get('mimeType') == 'application/vnd.google-apps.folder':
                    pass
                else:
                    print(F'Found file: {file.get("name")}, {file.get("id")}, {file.get("mimeType")}')
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    return files


def upload_file():
    creds = main()

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': 'My Report',
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaFileUpload('report.csv', mimetype='text/csv',
                                resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File with ID: "{file.get("id")}" has been uploaded.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')
