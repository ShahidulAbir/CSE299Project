from __future__ import print_function

import io
import os.path
import time

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from mimetypes import guess_type
from cryptography.fernet import Fernet
from users.models import Profile

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/drive']


def main(request):
    creds = None

    SCOPES = ['https://www.googleapis.com/auth/drive']

    if request.user.profile.token_file.name != 'default_token.json':
        creds = Credentials.from_authorized_user_file(request.user.profile.token_file.path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                request.user.profile.credentials_file.path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        file = open('media/token/' + request.user.username + '_token.json', "w")
        file.close()

        with open(request.user.profile.token_file.path, 'w') as token:
            token.write(creds.to_json())

    return creds


def create_folder_helper(request):
    creds = main(request)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        if request.user.profile.rootFolder == "":
            file_metadata = {
                'name': request.POST['folder_name'],
                'mimeType': 'application/vnd.google-apps.folder'
            }
        else:
            file_metadata = {
                'name': request.POST['folder_name'],
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [request.user.profile.rootFolder]
            }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder ID: "{file.get("id")}".')

        # if request.user.profile.rootFolder == "":
        #     print("hit")
        #     our_profile = Profile.objects.get(user=request.user)
        #     our_profile.rootFolder = file.get("id")
        #     our_profile.save()

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def upload_file_helper(request):
    creds = main(request)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        mimetype = guess_type(file_name)[0]

        with default_storage.open('temporary_storage/' + file_name, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        path = str(destination)

        secret = request.user.profile.secret_key
        fernet = Fernet(secret.encode("utf-8"))

        with open(path, 'rb') as f:
            content = f.read()

        encrypted = fernet.encrypt(content)

        with open(path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

        file_metadata = {
            'name': file_name,
            'mimeType': mimetype,
            # 'parents': [folder_id]
        }
        media = MediaFileUpload(path, mimetype=mimetype,
                                resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File with ID: "{file.get("id")}" has been uploaded.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')


def list_file_helper(request):
    creds = main(request)

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


def download_file_helper(request, file_id):
    creds = main(request)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        # file_id = file_id

        # pylint: disable=maybe-no-member
        request = service.files().export_media(fileId=file_id,
                                               mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml'
                                                        '.sheet')
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


def list_folder_helper(request):
    creds = main(request)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        folders = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            query = f"mimeType = 'application/vnd.google-apps.folder'"
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
            folders.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except HttpError as error:
        print(F'An error occurred: {error}')
        folders = None

    return folders
