from azure.identity import ClientSecretCredential
# import the dotenv module
from dotenv import load_dotenv
import os

# Load environment variables from .env file into script's environment
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID") 
client_secret =  os.getenv("CLIENT_SECRET") 
scope = 'https://analysis.windows.net/powerbi/api/.default'


# ---------------------------------------
# Option 3 for getting the token. If authenticating via client/client_secret
# ---------------------------------------
client_secret_credential_class = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

access_token_class = client_secret_credential_class.get_token(scope)
token_string = access_token_class.token


from pbipy import PowerBI

pbi = PowerBI(token_string)

admin = pbi.admin()

print(admin)

users = admin.report_users("5b218778-e7a5-4d73-8187-f10824047715")
print(users[0])