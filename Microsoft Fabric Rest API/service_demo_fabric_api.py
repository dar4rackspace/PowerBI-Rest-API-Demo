from azure.identity import ClientSecretCredential
import requests
# import the dotenv module
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from .env file into script's environment
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID") 
client_secret =  os.getenv("CLIENT_SECRET")
scope = 'https://api.fabric.microsoft.com/.default'
client_secret_credential_class = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
access_token_class = client_secret_credential_class.get_token(scope)
token_string = access_token_class.token

header = {'Content-Type':'application/json','Authorization': f'Bearer {token_string}'}

# Get workspaces
response = requests.get(url='https://api.fabric.microsoft.com/v1/workspaces', headers=header)

df = pd.json_normalize(response.json(), 'value')
print(df)

# List Items in Workspace
workspace_id = '75eeb7d8-9297-4adc-ad37-bcd05adbcedc' # BI Migration Test WS
response = requests.get(url=f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items', headers=header)

df = pd.json_normalize(response.json(), 'value')
print(df)

# List Items Admin API....No permission
# response = requests.get(url='https://api.fabric.microsoft.com/v1/Admin/items', headers=header)

# print(response)

# df = pd.json_normalize(response.json(), 'itemEntities')
# print(df)