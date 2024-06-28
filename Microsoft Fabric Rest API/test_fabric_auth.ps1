# Parameters 
$workspaceName = "POC Test"
$pbipSemanticModelPath = "C:\Users\dani7078\OneDrive - Rackspace Inc\Desktop\power_bi\Quality Review\Quality Review.SemanticModel" #"[PBIP Path]\[Item Name].SemanticModel"
$pbipReportPath = "C:\Users\dani7078\OneDrive - Rackspace Inc\Desktop\power_bi\Quality Review\Quality Review.Report" #"[PBIP Path]\[Item Name].Report"
$currentPath = (Split-Path $MyInvocation.MyCommand.Definition -Parent)
Set-Location $currentPath

# Function to load environment variables from .env file
function LoadDotEnv {
    param(
        [string]$envFile
    )

    # Read lines from the .env file
    $lines = Get-Content -Path $envFile

    foreach ($line in $lines) {
        if ($line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$key" -Value $value
        }
    }
}

# Load environment variables from secrets.env file
$envFilePath = "../.env"
LoadDotEnv -envFile $envFilePath

# Access the loaded environment variables
$CLIENT_ID = $env:CLIENT_ID
$CLIENT_SECRET = $env:CLIENT_SECRET
$TENANT_ID = $env:TENANT_ID
# # Example usage
Write-Output "CLIENT_ID: $CLIENT_ID"
Write-Output "CLIENT_SECRET: $CLIENT_SECRET"
Write-Output "TENANT_ID: $TENANT_ID"


# Download modules and install
New-Item -ItemType Directory -Path ".\modules" -ErrorAction SilentlyContinue | Out-Null
@("https://raw.githubusercontent.com/microsoft/Analysis-Services/master/pbidevmode/fabricps-pbip/FabricPS-PBIP.psm1"
, "https://raw.githubusercontent.com/microsoft/Analysis-Services/master/pbidevmode/fabricps-pbip/FabricPS-PBIP.psd1") |% {
    Invoke-WebRequest -Uri $_ -OutFile ".\modules\$(Split-Path $_ -Leaf)"
}
if(-not (Get-Module Az.Accounts -ListAvailable)) { 
    Install-Module Az.Accounts -Scope CurrentUser -Force
}
Import-Module ".\modules\FabricPS-PBIP" -Force

# Authenticate With service principal (spn)
Set-FabricAuthToken -servicePrincipalId $CLIENT_ID -servicePrincipalSecret $CLIENT_SECRET -tenantId 'raxglobal.onmicrosoft.com' -reset

# Ensure workspace exists
$workspaceId = New-FabricWorkspace  -name $workspaceName -skipErrorIfExists

# Import the semantic model and save the item id
$semanticModelImport = Import-FabricItem -workspaceId $workspaceId -path $pbipSemanticModelPath

# Import the report and ensure its binded to the previous imported report
$reportImport = Import-FabricItem -workspaceId $workspaceId -path $pbipReportPath -itemProperties @{"semanticModelId" = $semanticModelImport.Id}


# Clean up by removing the environment variables from memory
Remove-Item env:CLIENT_ID
Remove-Item env:CLIENT_SECRET