from azure.identity import ClientSecretCredential
import requests
from dotenv import load_dotenv
import os
import pandas as pd

def get_azure_token():
    try:
        # Load environment variables from .env file into script's environment
        load_dotenv()

        tenant_id = os.getenv("TENANT_ID")
        client_id = os.getenv("CLIENT_ID") 
        client_secret = os.getenv("CLIENT_SECRET")
        scope = 'https://api.fabric.microsoft.com/.default'
        
        # Authenticate and get access token
        client_secret_credential_class = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        access_token_class = client_secret_credential_class.get_token(scope)
        return access_token_class.token
    
    except Exception as e:
        print(f"Error occurred while getting Azure token: {e}")
        return None

def get_list_all_workspaces(token):
    try:
        # Build request headers with the provided token
        header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        # Make API request to get workspaces
        response = requests.get(url='https://api.fabric.microsoft.com/v1/workspaces', headers=header)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        
        # Normalize JSON response into a DataFrame
        df = pd.json_normalize(response.json(), 'value')
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        return None
    
    except Exception as e:
        print(f"Error occurred while fetching workspaces: {e}")
        return None


def create_new_workspace(name, access_token, skip_error_if_exists=False):
    try:
        api_url = 'https://api.fabric.microsoft.com/v1/workspaces'

        # Check if workspace exists
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        workspaces = response.json()['value']

        existing_workspace = next((ws for ws in workspaces if ws['displayName'].lower() == name.lower()), None)

        if existing_workspace:
            if skip_error_if_exists:
                print(f"Workspace '{name}' already exists")
                return existing_workspace['id']
            else:
                raise Exception(f"Workspace '{name}' already exists")

        # Create new workspace
        item_request = {
            'displayName': name
        }
        response = requests.post(api_url, headers=headers, json=item_request)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        
        created_workspace = response.json()
        print(f"Workspace created: '{name}'")
        return created_workspace['id']
    
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        return None
    
    except Exception as e:
        print(f"Error occurred while creating or checking workspace: {e}")
        return None
    
def delete_workspace_by_id(workspace_id, access_token):
    try:
        # Azure API endpoint
        api_url = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}'

        # Send DELETE request to delete workspace
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

        if response.status_code == 200:
            print(f"Workspace with ID '{workspace_id}' deleted successfully.")
        else:
            print(f"Unexpected status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
    
    except Exception as e:
        print(f"Error occurred while deleting workspace: {e}")

# Example usage:
if __name__ == "__main__":
    token = get_azure_token()
    # workspaces_df = get_list_all_workspaces(token)
    # print(workspaces_df)
    workspace_name = "MyNewWorkspace"
    created_workspace_id = create_new_workspace(workspace_name, token, skip_error_if_exists=True)
    
    if created_workspace_id:
        print(f"Created workspace ID: {created_workspace_id}")
    else:
        print("Failed to create workspace.")
    
    workspace_id_to_delete = created_workspace_id
    delete_workspace_by_id(workspace_id_to_delete, token)