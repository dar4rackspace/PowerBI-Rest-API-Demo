# source https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/deploy-project
from azure.identity import ClientSecretCredential
# import the dotenv module
from dotenv import load_dotenv
import os

# double check service account app has permissions https://learn.microsoft.com/en-us/rest/api/fabric/articles/scopes
# Load environment variables from .env file into script's environment
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID") 
client_secret =  os.getenv("CLIENT_SECRET") 
# i think its the most wide type of permissions
scopes = "https://api.fabric.microsoft.com/Workspace.ReadWrite.All https://api.fabric.microsoft.com/Item.ReadWrite.All"
scope = 'https://analysis.windows.net/powerbi/api/.default'

# list items: The caller must have viewer or higher workspace role. Workspace.Read.All or Workspace.ReadWrite.All

# create item

# update item definition


# raw request
from azure.identity import ClientSecretCredential
import requests

def authenticate_client(tenant_id, client_id, client_secret, scope):
    try:
        # Create ClientSecretCredential instance
        client_secret_credential = ClientSecretCredential(
            authority = 'https://login.microsoftonline.com/',
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        # Get access token
        access_token_class = client_secret_credential.get_token(scope)
        access_token = access_token_class.token

        return access_token

    except Exception as e:
        print(f"Error authenticating client: {e}")
        return None
    
    
def get_groups(token):
    # Define endpoint and headers
    url = 'https://api.powerbi.com/v1.0/myorg/groups'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    try:
        # Make GET request to Power BI API
        response = requests.get(url, headers=headers)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            groups = response.json()['value']
            return groups
        else:
            print(f"Failed to retrieve groups. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching groups: {e}")
        return None


def get_datasets(token):
    # Define endpoint and headers
    url = 'https://api.powerbi.com/v1.0/myorg/datasets'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    try:
        # Make GET request to Power BI API
        response = requests.get(url, headers=headers)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            datasets = response.json()['value']
            return datasets
        else:
            print(f"Failed to retrieve datasets. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching datasets: {e}")
        return None

import requests

def refresh_dataset(token, dataset_id):
    # Define endpoint and headers
    url = f'https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    # Request body (optional, based on API documentation)
    # Modify as per your requirements (notifyOption, applyRefreshPolicy, etc.)
    body = {
        'notifyOption': 'MailOnCompletion',  # Example notifyOption, modify as needed
        'applyRefreshPolicy': True,  # Example applyRefreshPolicy, modify as needed
        'retryCount': 1  # Example retryCount, modify as needed
        # Add more parameters as required
    }

    try:
        # Make POST request to trigger dataset refresh
        response = requests.post(url, headers=headers, json=body)

        # Check if request was successful (status code 202 Accepted)
        if response.status_code == 202:
            refresh_id = response.headers.get('Location')
            print(f"Dataset refresh triggered successfully. Refresh ID: {refresh_id}")
            return refresh_id
        else:
            print(f"Failed to trigger dataset refresh. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error triggering dataset refresh: {e}")
        return None


def create_group(token, group_name):
    # Define endpoint and headers
    url = 'https://api.powerbi.com/v1.0/myorg/groups'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    # Request body
    body = {
        'name': group_name
    }

    try:
        # Make POST request to create a new group
        response = requests.post(url, headers=headers, json=body)

        # Check if request was successful (status code 201 Created)
        if response.status_code == 201:
            group_id = response.json()['id']
            print(f"Group '{group_name}' created successfully. Group ID: {group_id}")
            return group_id
        else:
            print(f"Failed to create group '{group_name}'. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error creating group: {e}")
        return None

def add_group_user(token, group_id, identifier=None, principal_type=None, display_name=None, email_address=None, graph_id=None, profile=None, user_type=None, group_user_access_right='Member'):
    """
    Adds a user to the specified workspace (group) in Power BI with the specified access rights.

    Args:
        token (str): Authorization token for API authentication.
        group_id (str): ID of the workspace (group) to add the user to.
        identifier (str, optional): Identifier of the principal (e.g., user ID or app ID).
        principal_type (str, optional): Principal type of the user ('App', 'Group', 'User').
        display_name (str, optional): Display name of the principal (user or app).
        email_address (str, optional): Email address of the user.
        graph_id (str, optional): Identifier of the principal in Microsoft Graph (for admin APIs).
        profile (dict, optional): Power BI service principal profile (relevant for Power BI Embedded multi-tenancy).
        user_type (str, optional): Type of the user.
        group_user_access_right (str, optional): Access rights (permission level) that the user should have on the workspace.
                                                Valid values: 'Admin', 'Contributor', 'Member', 'Viewer', 'None'.

    Returns:
        bool: True if user was added successfully, False otherwise.
    """
    # Define endpoint and headers
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{group_id}/users'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    # Request body
    body = {
        'groupUserAccessRight': group_user_access_right
    }

    # Add optional parameters to request body
    if identifier:
        body['identifier'] = identifier
    if principal_type:
        body['principalType'] = principal_type
    if display_name:
        body['displayName'] = display_name
    if email_address:
        body['emailAddress'] = email_address
    if graph_id:
        body['graphId'] = graph_id
    if profile:
        body['profile'] = profile
    if user_type:
        body['userType'] = user_type

    try:
        # Make POST request to add user to group
        response = requests.post(url, headers=headers, json=body)

        # Check if request was successful (status code 200 OK)
        if response.status_code == 200:
            print(f"User added successfully to group '{group_id}'.")
            return True
        else:
            print(f"Failed to add user to group '{group_id}'. Status code: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error adding user to group: {e}")
        return False



def refresh_user_permissions(token):
    """
    Refreshes user permissions in Power BI to ensure they're fully updated before making other API calls.

    Args:
        token (str): Authorization token for API authentication.

    Returns:
        bool: True if user permissions were successfully refreshed, False otherwise.
    """
    # Define endpoint and headers
    url = 'https://api.powerbi.com/v1.0/myorg/RefreshUserPermissions'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    try:
        # Make POST request to refresh user permissions
        response = requests.post(url, headers=headers)

        # Check if request was successful (status code 200 OK)
        if response.status_code == 200:
            print("User permissions refreshed successfully.")
            return True
        else:
            print(f"Failed to refresh user permissions. Status code: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error refreshing user permissions: {e}")
        return False

# Example usage:
# Replace 'your_token_here' with an actual Power BI access token obtained through authentication.
# refresh_user_permissions('your_token_here')
