import requests
from dotenv import load_dotenv
import os

def add_user_to_workspace(workspace_id, user_id, role):
    try:
        # Load environment variables from .env file into script's environment
        load_dotenv()

        # Azure credentials and API endpoint
        tenant_id = os.getenv("TENANT_ID")
        client_id = os.getenv("CLIENT_ID") 
        client_secret = os.getenv("CLIENT_SECRET")
        scope = 'https://api.fabric.microsoft.com/.default'
        api_url = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/roleAssignments'

        # Authenticate and get access token
        from azure.identity import ClientSecretCredential
        client_secret_credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        access_token = client_secret_credential.get_token(scope).token

        # Prepare request body
        request_body = {
            "principal": {
                "id": user_id,
                "type": "User"
            },
            "role": role
        }

        # Send POST request to add user to workspace
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.post(api_url, headers=headers, json=request_body)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

        if response.status_code == 201:
            print(f"User '{user_id}' added to workspace '{workspace_id}' with role '{role}' successfully.")
            return response.json()
        else:
            print(f"Unexpected status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
    
    except Exception as e:
        print(f"Error occurred while adding user to workspace: {e}")

# Example usage:
if __name__ == "__main__":
    workspace_id = "fdd80fc9-49d9-4fb5-9e1a-f080565c9c62" #"337e2d10-88de-40ae-9a75-08cc7dd46a3a" #"5d39c3c1-2981-4813-85c6-2be841b580e9"  # Replace with the actual workspace ID
    user_id = "f19d236d-0e8b-484b-a8ab-a625bb667ab0" #"b88fabd2-a643-4d2c-a109-e489101028a9"  # Replace with the actual user ID
    role = "Member"  # Specify the role you want to assign

    add_user_to_workspace(workspace_id, user_id, role)
