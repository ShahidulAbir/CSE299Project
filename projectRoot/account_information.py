from Google import Create_Service
from pprint import pprint

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

response = service.about().get(fields='*').execute()
pprint(response)

for k, v in response.get('storageQuota').items():
    print('{0}: {1:.2f}MB'.format(k, int(v) / 1024**2))
    print('{0}: {1:.2f}GB'.format(k, int(v) / 1024**3))
