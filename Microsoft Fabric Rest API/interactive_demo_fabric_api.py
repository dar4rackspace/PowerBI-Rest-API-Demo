import mssparkutils
import requests

import requests
token_string = mssparkutils.credentials.getToken("https://api.fabric.microsoft.com/")
header = {'Content-Type':'application/json','Authorization': f'Bearer {token_string}'}
response = requests.get(url='https://api.fabric.microsoft.com/v1/workspaces', headers=header)

header = {'Content-Type':'application/json','Authorization': f'Bearer {token_string}'}
response = requests.get(url='https://api.fabric.microsoft.com/v1/workspaces', headers=header)