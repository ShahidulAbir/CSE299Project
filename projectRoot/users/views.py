from __future__ import print_function

import mimetypes

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

from django.http import HttpResponse, FileResponse
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin


import sys
import os
# import comtypes.client
import pathlib
import win32com.client
import pythoncom


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
        file_request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, file_request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    with open('templates/account/static/downloads/' + file_name, 'wb') as f:
        f.write(file.getvalue())

    secret = User.objects.get(username=user).profile.secret_key
    fernet = Fernet(secret.encode("utf-8"))

    with open('templates/account/static/downloads/' + file_name, 'rb') as f:
        content = f.read()

    decrypted = fernet.decrypt(content)

    with open('templates/account/static/downloads/' + file_name, 'wb') as decrypted_file:
        decrypted_file.write(decrypted)

    # return file.getvalue()
    # context = {'file_name': file_name}
    #

    with open('templates/account/static/downloads/' + file_name, 'rb') as read_file:
        file_data = read_file.read()

    file_type = mimetypes.guess_type(file_name)[0]
    file_name_without_extension = pathlib.Path(file_name).stem

    if file_type == 'application/msword' or file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        wdFormatPDF = 17

        in_file = os.path.abspath('templates/account/static/downloads/' + file_name)
        out_file = os.path.abspath('templates/account/static/downloads/' + file_name_without_extension + '.pdf')

        word = win32com.client.Dispatch('Word.Application', pythoncom.CoInitialize())
        doc = word.Documents.Open(in_file)
        doc.SaveAs(out_file, FileFormat=wdFormatPDF)
        doc.Close()
        word.Quit()

    elif file_type == 'application/vnd.ms-excel' or file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        in_file = os.path.abspath('templates/account/static/downloads/' + file_name)
        out_file = os.path.abspath('templates/account/static/downloads/' + file_name_without_extension + '.pdf')

        excel = win32com.client.Dispatch("Excel.Application", pythoncom.CoInitialize())
        sheets = excel.Workbooks.Open(in_file)
        work_sheets = sheets.Worksheets[0]

        work_sheets.ExportAsFixedFormat(0, out_file)

    elif file_type == 'application/vnd.ms-powerpoint' or file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        in_file = os.path.abspath('templates/account/static/downloads/' + file_name)
        out_file = os.path.abspath('templates/account/static/downloads/' + file_name_without_extension + '.pdf')

        powerpoint = win32com.client.Dispatch("Powerpoint.Application", pythoncom.CoInitialize())
        powerpoint.Visible = 1

        deck = powerpoint.Presentations.Open(in_file)
        deck.SaveAs(out_file, FileFormat=32)  # formatType = 32 for ppt to pdf
        deck.Close()
        powerpoint.Quit()

    file_name = file_name_without_extension + '.pdf'

    return render(request, 'account/file2.html', {'file_name': file_name})


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

@login_required
@xframe_options_exempt
def preview(request, file_name):
    return render(request, 'account/preview.html', context={'file_name': file_name})


@login_required
def face_detect(request):
    # This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
    # other example, but it includes some basic performance tweaks to make things run a lot faster:
    #   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
    #   2. Only detect faces in every other frame of video.

    # PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
    # OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
    # specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    shahidul_image = face_recognition.load_image_file("Shahidul.jpg")
    shahidul_face_encoding = face_recognition.face_encodings(shahidul_image)[0]

    # Load a second sample picture and learn how to recognize it.
    arnop_image = face_recognition.load_image_file("Arnop.jpg")
    arnop_face_encoding = face_recognition.face_encodings(arnop_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        shahidul_face_encoding,
        arnop_face_encoding
    ]
    known_face_names = [
        "Shahidul Islam",
        "Arnop Singh"
    ]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        print("True")

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


@login_required
@xframe_options_sameorigin
def detection(request):
    return render(request, 'account/file2.html')

# @login_required
# def file2(request):
#     return render(request, 'account/file2.html')
