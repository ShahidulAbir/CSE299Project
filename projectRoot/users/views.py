from __future__ import print_function

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileUpdateForm, UploadFileForm
from django.contrib import messages

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
from cryptography.fernet import Fernet

from .helper_methods import main, upload_file_helper, create_folder_helper, list_file_helper, list_folder_helper


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
    return render(request, 'account/add_folder.html')


@login_required
def create_folder_call(request):
    create_folder_helper(request)

    return redirect('profile')


@login_required
def download_file(request, user, file_id, file_name):
    creds = main(request)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        # file_id = file_id  # real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    with open('media/downloads/' + file_name, 'wb') as f:
        f.write(file.getvalue())

    secret = User.objects.get(username=user).profile.secret_key
    fernet = Fernet(secret.encode("utf-8"))

    with open('media/downloads/' + file_name, 'rb') as f:
        content = f.read()

    decrypted = fernet.decrypt(content)

    with open('media/downloads/' + file_name, 'wb') as decrypted_file:
        decrypted_file.write(decrypted)

    # return file.getvalue()

    return redirect('profile')


@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            print("Valid")
            form.instance.owner = request.user
            form.save()

            upload_file_helper(request)

        return redirect('profile')
    else:
        form = UploadFileForm()

    context = {'form': form}

    return render(request, 'account/upload_file.html', context)


@login_required
def list_files(request):
    files = list_file_helper(request)

    return render(request, 'account/files.html', {'files': files})


# @login_required
# def downloading(request):
#     return render(request, 'account/drive.html', {'files': files})

# @login_required
# def select_folder(request):
#     if request.user.profile.rootFolder == "":
#         return render(request, 'account/add_folder.html')
#     else:
#         folders = list_folder_helper(request)
#         return render(request, 'account/folders.html', {'folders': folders})
