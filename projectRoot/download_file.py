import os
import io
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

file_ids = ['1MBmIJe1E3oHb-K1Zd2b5bvDg1aklQ5sb', '1wYQqZ0NOkH7eGpnXoI6fFLpI6H']
file_names = ['text.xlsx', 'photo.jpeg']

for file_id, filename in zip(file_ids, file_names):
    request = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)

    with open(os.path.join('', filename), 'wb') as f:
        f.write(fh.read())
        f.close()
