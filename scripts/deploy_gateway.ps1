# PowerShell Script for API Gateway Deployment
# Replicates the logic of deploy_gateway.sh for Windows environments

param (
    [Parameter(Mandatory=$true)]
    [string]$ProjectId
)

$ErrorActionPreference = "Stop"

# Configuration
$ApiId = "borrow-api"
$GatewayId = "borrow-gateway"
$Region = "us-central1"
$ServiceAccount = "ai-assistant-cloud-run-sa@teak-strength-485420-v3.iam.gserviceaccount.com"
$ConfigFile = "api_gateway_config.yaml"

Write-Host "Deploying API Gateway configuration for Project: $ProjectId"

# 1. Calculate SHA256 hash (truncated to 63 chars)
if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file '$ConfigFile' not found."
    exit 1
}

$HashObj = [System.Security.Cryptography.SHA256]::Create()
$Stream = [System.IO.File]::OpenRead((Resolve-Path $ConfigFile))
$HashBytes = $HashObj.ComputeHash($Stream)
$Stream.Close()
$FullHash = [BitConverter]::ToString($HashBytes) -replace "-"
$ConfigHash = $FullHash.Substring(0, 63).ToLower()

Write-Host "Config Hash: $ConfigHash"

# 2. Check for ANY existing config with this hash (via labels)
Write-Host "Checking for existing config with matching hash..."

$ExistingConfigsJson = gcloud api-gateway api-configs list --api=$ApiId --project=$ProjectId --format="json" | Out-String | ConvertFrom-Json

$ExistingConfigId = $null
if ($ExistingConfigsJson) {
    foreach ($config in $ExistingConfigsJson) {
        if ($config.labels -and $config.labels.'content-hash' -eq $ConfigHash) {
            $ExistingConfigId = $config.name.Split("/")[-1]
            break
        }
    }
}

if ($ExistingConfigId) {
    $TargetConfigId = $ExistingConfigId
    Write-Host "Found existing config with matching content: $TargetConfigId"
} else {
    Write-Host "No existing config found with matching content hash."

    # 3. Determine Next Version Number
    Write-Host "Determining next version number..."

    $MaxVersion = 0
    if ($ExistingConfigsJson) {
        foreach ($config in $ExistingConfigsJson) {
            $ConfigName = $config.name.Split("/")[-1]
            if ($ConfigName -match '^borrow-config-v(\d+)(-.*)?$') {
                $Version = [int]$matches[1]
                if ($Version -gt $MaxVersion) {
                    $MaxVersion = $Version
                }
            }
        }
    }

    $NextVersion = $MaxVersion + 1
    $TargetConfigId = "borrow-config-v$NextVersion"
    Write-Host "Next Version: $NextVersion"
    Write-Host "Creating new API Config: $TargetConfigId"

    # 4. Create New Config with Hash Label
    gcloud api-gateway api-configs create $TargetConfigId `
        --api=$ApiId `
        --openapi-spec=$ConfigFile `
        --project=$ProjectId `
        --backend-auth-service-account=$ServiceAccount `
        --labels="content-hash=$ConfigHash"
}

# 5. Check if Gateway update is needed
$CurrentConfigFull = gcloud api-gateway gateways describe $GatewayId --location=$Region --project=$ProjectId --format="value(apiConfig)"
$CurrentConfigId = $CurrentConfigFull.Split("/")[-1]

Write-Host "Current Gateway Config: $CurrentConfigId"
Write-Host "Target Gateway Config:  $TargetConfigId"

if ($CurrentConfigId -eq $TargetConfigId) {
    Write-Host "Success: Gateway is already serving the target configuration."
    exit 0
} else {
    Write-Host "Updating Gateway to use $TargetConfigId..."
    gcloud api-gateway gateways update $GatewayId `
        --api=$ApiId `
        --api-config=$TargetConfigId `
        --location=$Region `
        --project=$ProjectId
    Write-Host "Gateway update initiated successfully."
}
