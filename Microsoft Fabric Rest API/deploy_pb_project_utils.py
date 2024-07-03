from azure.identity import ClientSecretCredential
import requests
from dotenv import load_dotenv
import os
import pandas as pd
import json
import base64

def get_azure_token():
    try:
        load_dotenv()  # Load environment variables from .env file

        tenant_id = os.getenv("TENANT_ID")
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        scope = 'https://api.fabric.microsoft.com/.default'

        credential = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        access_token = credential.get_token(scope)
        return access_token.token

    except Exception as e:
        print(f"Error occurred while getting Azure token: {e}")
        return None


def find_pbip_file(path):
    for root, _, files in os.walk(path):
        for file_name in files:
            if file_name.endswith(".pbir"):
                return os.path.join(root, file_name), "Report"
            elif file_name.endswith(".pbism"):
                return os.path.join(root, file_name), "SemanticModel"
    return None, None

def import_fabric_itemv1(workspace_id, path, item_properties=None):
    try:
        pbip_path, item_type = find_pbip_file(path)
        print("Found files:")
        print(pbip_path)

        if not pbip_path or not item_type:
            raise ValueError("Cannot find valid item definitions (*.pbir; *.pbism) in the specified folder.")

        item_path = os.path.dirname(pbip_path)  # Get the directory containing the found item file
        
        access_token = get_azure_token()
        print("Got token")

        if not access_token:
            return "Missing access token!"

        # Get existing items of the workspace
        api_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        print("Listing items")
        response = requests.get(api_url, headers=headers)
        items = response.json()
        print(f"Existing items in the workspace: {len(items)}")

        # Prepare parts (files)
        parts = process_files(item_path, [], {})  # Pass item_path to process_files

        # Prepare item properties
        display_name = None
        if item_properties and "displayName" in item_properties:
            display_name = item_properties["displayName"]

        # Check if item already exists
        found_item = next((item for item in items if isinstance(item, dict) and
                           item.get("type", "").lower() == item_type.lower() and
                           item.get("displayName", "").lower() == display_name.lower()), None)

        if found_item:
            if len(items) > 1:
                raise ValueError(f"Found more than one item for displayName '{display_name}'")

            print(f"Item '{display_name}' of type '{item_type}' already exists.")
            item_id = found_item["id"]
        else:
            print("Creating a new item")
            
            # Default display name or this should not be here?
            display_name = 'Test'

            item_request = {
                "displayName": display_name,
                "type": item_type,
                "definition": {
                    "Parts": parts
                }
            }

            
            print("Made dictionary")

            item_request_json = json.dumps(item_request, indent=3)
            print("Made JSON")

            try:
                response = requests.post(api_url, headers=headers, json=item_request)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

                response_json = response.json()
                item_id = response_json["id"]
                print(f"Created a new item with ID '{item_id}'")

            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.content}")
                return None

        # Update item definition if necessary
        if item_id:
            print("Updating item definition")
            update_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{item_id}/updateDefinition"
            update_request = {
                "definition": {
                    "Parts": parts
                }
            }
            response = requests.post(update_url, headers=headers, json=update_request)
            print(f"Updated item with ID '{item_id}'")

        return {
            "id": item_id,
            "displayName": display_name,
            "type": item_type
        }

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def process_files(path, fileOverridesEncoded, datasetReferences):
    parts = []
    
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            
            file_override_match = None
            
            # Check if there's a file override match
            if fileOverridesEncoded:
                file_override_match = next((fo for fo in fileOverridesEncoded if file_path.lower() == fo["Name"].lower()), None)
            
            if file_override_match:
                print(f"File override '{file_name}'")
                file_content = base64.b64decode(file_override_match["Value"])
            else:
                if file_name.endswith(".pbir"):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content_text = f.read()
                        pbir_json = json.loads(file_content_text)
                        
                        if pbir_json.get("datasetReference", {}).get("byPath", {}).get("path"):
                            report_dataset_path = os.path.join(path, pbir_json["datasetReference"]["byPath"]["path"].replace("/", "\\"))
                            
                            dataset_reference = datasetReferences.get(report_dataset_path)
                            
                            if dataset_reference:
                                dataset_id = dataset_reference["id"]
                                
                                pbir_json["datasetReference"]["byPath"] = None
                                pbir_json["datasetReference"]["byConnection"] = {
                                    "connectionString": None,
                                    "pbiServiceModelId": None,
                                    "pbiModelVirtualServerName": "sobe_wowvirtualserver",
                                    "pbiModelDatabaseName": str(dataset_id),
                                    "name": "EntityDataSource",
                                    "connectionType": "pbiServiceXmlaStyleLive"
                                }
                                
                                new_pbir = json.dumps(pbir_json)
                                file_content = new_pbir.encode('utf-8')
                            else:
                                raise Exception("Item API doesn't support byPath connection, switch the connection in the *.pbir file to 'byConnection'.")
                        else:
                            file_content = file_content_text.encode('utf-8')
                else:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
            
            part_path = os.path.relpath(file_path, path).replace("\\", "/")
            file_encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            parts.append({
                "Path": part_path,
                "Payload": file_encoded_content,
                "PayloadType": "InlineBase64"
            })
    
    #print("Payload parts:")
    # for part in parts:
    #     print(f"part: {part['Path']}")
    
    return parts



# def import_fabric_itemv2(workspace_id, pbip_path, item_properties=None):
#     try:
#         access_token = get_azure_token()
#         if not access_token:
#             return

#         # Determine item type (Report or SemanticModel)
#         if pbip_path.endswith(".pbir"):
#             item_type = "Report"
#         elif pbip_path.endswith(".pbism"):
#             item_type = "SemanticModel"
#         else:
#             raise ValueError("Unsupported file format. Supported formats are .pbir and .pbism.")

#         # Get existing items of the workspace
#         api_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items"
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }
#         response = requests.get(api_url, headers=headers)
#         items = response.json()

#         print(f"Existing items in the workspace: {len(items)}")

#         # Prepare parts (files)
#         with open(pbip_path, "rb") as f:
#             file_content = f.read()
#             part_path = os.path.basename(pbip_path)
#             parts = [{
#                 "Path": part_path,
#                 "Payload": file_content,
#                 "PayloadType": "InlineBase64"
#             }]

#         print("Payload parts:")
#         print(f"part: {part_path}")

#         # Prepare item properties
#         display_name = None
#         if item_properties and "displayName" in item_properties:
#             display_name = item_properties["displayName"]

#         # Check if item already exists
#         found_item = next((item for item in items if item["type"].lower() == item_type.lower() and
#                            item["displayName"].lower() == display_name.lower()), None)

#         if found_item:
#             if len(items) > 1:
#                 raise ValueError(f"Found more than one item for displayName '{display_name}'")

#             print(f"Item '{display_name}' of type '{item_type}' already exists.")
#             item_id = found_item["id"]
#         else:
#             print("Creating a new item")
#             item_request = {
#                 "displayName": display_name,
#                 "type": item_type,
#                 "definition": {
#                     "Parts": parts
#                 }
#             }
#             response = requests.post(api_url, headers=headers, json=item_request)
#             response_json = response.json()
#             item_id = response_json["id"]

#             print(f"Created a new item with ID '{item_id}'")

#         # Update item definition if necessary
#         if item_id:
#             print("Updating item definition")
#             update_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{item_id}/updateDefinition"
#             update_request = {
#                 "definition": {
#                     "Parts": parts
#                 }
#             }
#             response = requests.post(update_url, headers=headers, json=update_request)
#             print(f"Updated item with ID '{item_id}'")

#         return {
#             "id": item_id,
#             "displayName": display_name,
#             "type": item_type
#         }

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return None



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
    workspaces_df = get_list_all_workspaces(token)
    print(workspaces_df)
    # workspace_name = "MyNewWorkspace"
    # created_workspace_id = create_new_workspace(workspace_name, token, skip_error_if_exists=True)
    
    # if created_workspace_id:
    #      print(f"Created workspace ID: {created_workspace_id}")
    # else:
    #      print("Failed to create workspace.")
    
    # workspace_id_to_delete = created_workspace_id
    #delete_workspace_by_id(workspace_id_to_delete, token)
    # Example usage:
    # workspace_id = "a82e8dce-f4d8-400f-b08c-0a577e7c2562"
    # pbip_report_path = "<path_to_pbip_report>"
    # pbip_semantic_path = r"C:\Users\dani7078\OneDrive - Rackspace Inc\Desktop\power_bi\Partner Analytics\Partner Analytics.SemanticModel" #"[PBIP Path]\[Item Name].SemanticModel"
    # item_properties = {
    #     "displayName": "<your_display_name>",
    #     "semanticModelId": "<semantic_model_id>"
    # }

    # import_fabric_itemv1(workspace_id, pbip_semantic_path, item_properties=None)

