from Google import Create_Service

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

folder_id = '1Z7u68Tx24x26FlbRfj11oIHogSfOc4B0'
query = f"parents = '{folder_id}'"

response = service.files().list(q=query).execute()
files = response.get('files')
nextPageToken = response.get('nextPageToken')
print(files)

while nextPageToken:
    response = service.files().list(q=query, pageToken=nextPageToken).execute()
    files.extend()
    nextPageToken = response.get('nextPageToken')

print(files)
