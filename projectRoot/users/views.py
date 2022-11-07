from __future__ import print_function

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileUpdateForm
from django.contrib import messages
from .drive_utilities import main

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


def homepage_redirect(request):
    return render(request, 'account/login.html')


@login_required
def show_profile(request):
    return render(request, 'account/drive.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            form.save()
            messages.success(request, f'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'form': form
    }

    return render(request, 'account/update_profile.html', context)


@login_required
def create_folder(request):
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
        with open(request.user.profile.token_file.path, 'w') as token:
            token.write(creds.to_json())

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=request.user.profile.credentials_file)
        file_metadata = {
            'name': request.POST["folder_name"],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder ID: "{file.get("id")}".')
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None

