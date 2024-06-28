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

# fabric workspace
# ADDED srevice security group
# print("Datasets")
# print(pbi.datasets(group="51ada905-6b70-4ab8-8416-75d4c33fca67"))
# print("Reports")
# print(pbi.reports(group="51ada905-6b70-4ab8-8416-75d4c33fca67"))
# admin = pbi.admin() #no admin permissions
# users = admin.report_users("51ada905-6b70-4ab8-8416-75d4c33fca67")
# print(users[0])

#  premoium
# print("Datasets")
# print(pbi.datasets(group="75eeb7d8-9297-4adc-ad37-bcd05adbcedc"))
# print("Reports")
# print(pbi.reports(group="75eeb7d8-9297-4adc-ad37-bcd05adbcedc"))
# admin = pbi.admin()
# users = admin.report_users("75eeb7d8-9297-4adc-ad37-bcd05adbcedc")
# print(users[0])

# MARKETING analytics premium
# print("Reports")
# print(pbi.reports(group="e6a3dd93-81f9-4e1d-b2bf-6ad9ef926589"))

# list workspafes
print("List workspaces")
groups = pbi.groups()

for group in groups:
    print(group)


group = pbi.group("51ada905-6b70-4ab8-8416-75d4c33fca67")
users = group.users()

for user in users:
    print(user)

# cant add users
#  "identifier": "1f69e798-5852-4fdd-ab01-33bb14b6e934",
# group.add_user(identifier='',email_address="guillermo.pereztello@rackspace.com", principal_type="User", access_right="Read")

# users = group.users()

# for user in users:
#     print(user)

# Give John 'Read' access on the dataset
sales = pbi.dataset(
    id="cfafbeb1-8037-4d0c-896e-a46fb27ff229",
    group="f089354e-8366-4e18-aea3-4cb4a3a50b48",
)

print(sales)
sales.add_user("john@contoso.com", "User", "Read")