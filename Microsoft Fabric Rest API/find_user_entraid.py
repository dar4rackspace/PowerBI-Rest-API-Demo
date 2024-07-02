import subprocess
from dotenv import load_dotenv
import os

load_dotenv()
# Define your Azure service principal credentials
app_id = os.getenv("CLIENT_ID") 
password_or_cert = os.getenv("CLIENT_SECRET")
tenant = os.getenv("TENANT_ID")
user_email = "daniel.amieva@rackspace.com"

# Login to Azure using service principal
# login_command = [
#     "az", "login",
#     "--service-principal",
#     "-u", app_id,
#     "-p", password_or_cert,
#     "--tenant", tenant
# ]
login_command = [
    r"C:\Users\dani7078\AppData\Local\miniconda3\envs\powerbi\Scripts\az.bat",  # Path to az.cmd in your environment
    #"az",
    "login",
    "--service-principal",
    "-u", app_id,
    "-p", password_or_cert,
    "--tenant", tenant
]
subprocess.run(login_command, stdout=subprocess.PIPE, check=True, env=os.environ)

print("retrieve data")
# Retrieve user information
get_user_command = [
    r"C:\Users\dani7078\AppData\Local\miniconda3\envs\powerbi\Scripts\az.bat",  "ad", "user", "show",
    "--id", user_email,
    "--query", "id",
    "--out", "tsv"
]
result = subprocess.run(get_user_command, stdout=subprocess.PIPE, check=True, env=os.environ)

# Extract the output from the command
user_id = result.stdout.decode('utf-8').strip()

print(f"User ID for {user_email}: {user_id}")
