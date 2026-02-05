# Script to manually update the API Gateway configuration
# This is required when new routes are added to api_gateway_config.yaml

$PROJECT_ID = "teak-strength-485420-v3"
$GATEWAY_ID = "borrow-gateway"
$REGION = "us-central1"
$SERVICE_ACCOUNT = "ai-assistant-cloud-run-sa@teak-strength-485420-v3.iam.gserviceaccount.com"
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$CONFIG_ID = "borrow-config-$TIMESTAMP"

Write-Host "=========================================="
Write-Host "Updating API Gateway: $GATEWAY_ID"
Write-Host "New Config ID: $CONFIG_ID"
Write-Host "=========================================="

# 1. Create a new API Config
Write-Host "`n[1/2] Creating new API Config..."
$createCmd = "gcloud api-gateway api-configs create $CONFIG_ID --api=$GATEWAY_ID --openapi-spec=api_gateway_config.yaml --project=$PROJECT_ID --backend-auth-service-account=$SERVICE_ACCOUNT"
Write-Host "Running: $createCmd"
Invoke-Expression $createCmd

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create API Config."
    exit 1
}

# 2. Update the Gateway to use the new Config
Write-Host "`n[2/2] Updating Gateway to use new config (this may take several minutes)..."
$updateCmd = "gcloud api-gateway gateways update $GATEWAY_ID --api=$GATEWAY_ID --api-config=$CONFIG_ID --location=$REGION --project=$PROJECT_ID"
Write-Host "Running: $updateCmd"
Invoke-Expression $updateCmd

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to update Gateway."
    exit 1
}

Write-Host "`n=========================================="
Write-Host "SUCCESS: API Gateway updated successfully!"
Write-Host "Base URL: https://$GATEWAY_ID-$REGION.gateway.dev"
Write-Host "Docs URL: https://$GATEWAY_ID-$REGION.gateway.dev/docs"
Write-Host "=========================================="
