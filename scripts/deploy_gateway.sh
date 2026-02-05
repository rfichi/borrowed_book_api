#!/bin/bash
set -e

# Configuration
PROJECT_ID=$1
API_ID="borrow-api"
GATEWAY_ID="borrow-gateway"
REGION="us-central1"
SERVICE_ACCOUNT="ai-assistant-cloud-run-sa@teak-strength-485420-v3.iam.gserviceaccount.com"
CONFIG_FILE="api_gateway_config.yaml"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID argument is required."
    exit 1
fi

echo "Deploying API Gateway configuration for Project: $PROJECT_ID"

# 1. Calculate SHA256 hash of the config file
# Truncate to 63 characters to meet GCP Label value requirements (max 63 chars)
if ! command -v sha256sum &> /dev/null; then
    echo "sha256sum not found, using python fallback"
    CONFIG_HASH=$(python3 -c "import hashlib; print(hashlib.sha256(open('$CONFIG_FILE', 'rb').read()).hexdigest()[:63])")
else
    CONFIG_HASH=$(sha256sum $CONFIG_FILE | awk '{print $1}' | cut -c 1-63)
fi
echo "Config Hash: $CONFIG_HASH"

# 2. Check for ANY existing config with this hash (via labels)
echo "Checking for existing config with matching hash..."
# We fetch all configs and filter client-side because the API might not support label filtering directly
EXISTING_CONFIG_FULL=$(gcloud api-gateway api-configs list \
    --api=$API_ID \
    --project=$PROJECT_ID \
    --format="json" | \
    python3 -c "
import sys, json
target_hash = '$CONFIG_HASH'
try:
    configs = json.load(sys.stdin)
    found = ''
    for c in configs:
        labels = c.get('labels', {})
        if labels.get('content-hash') == target_hash:
            found = c['name']
            break
    print(found)
except Exception as e:
    # In case of empty list or error, print nothing
    pass
")

if [ -n "$EXISTING_CONFIG_FULL" ]; then
    TARGET_CONFIG_ID=$(basename "$EXISTING_CONFIG_FULL")
    echo "Found existing config with matching content: $TARGET_CONFIG_ID"
else
    echo "No existing config found with matching content hash."

    # 3. Determine Next Version Number
    echo "Determining next version number..."
    # List all config IDs, filter for 'borrow-config-v*', extract version numbers, find max
    # We use python for robust version parsing to avoid complex shell regex compatibility issues
    MAX_VERSION=$(gcloud api-gateway api-configs list \
        --api=$API_ID \
        --project=$PROJECT_ID \
        --format="value(name)" | \
        while read line; do basename "$line"; done | \
        python3 -c "
import sys, re
max_v = 0
pattern = re.compile(r'^borrow-config-v(\d+)(-.*)?$')
for line in sys.stdin:
    line = line.strip()
    match = pattern.match(line)
    if match:
        v = int(match.group(1))
        if v > max_v:
            max_v = v
print(max_v)
")

    NEXT_VERSION=$((MAX_VERSION + 1))
    TARGET_CONFIG_ID="borrow-config-v${NEXT_VERSION}"
    echo "Next Version: $NEXT_VERSION"
    echo "Creating new API Config: $TARGET_CONFIG_ID"

    # 4. Create New Config with Hash Label
    gcloud api-gateway api-configs create $TARGET_CONFIG_ID \
        --api=$API_ID \
        --openapi-spec=$CONFIG_FILE \
        --project=$PROJECT_ID \
        --backend-auth-service-account=$SERVICE_ACCOUNT \
        --labels=content-hash=$CONFIG_HASH
fi

# 5. Check if Gateway update is needed
CURRENT_CONFIG_FULL=$(gcloud api-gateway gateways describe $GATEWAY_ID --location=$REGION --project=$PROJECT_ID --format="value(apiConfig)")
CURRENT_CONFIG_ID=$(basename "$CURRENT_CONFIG_FULL")

echo "Current Gateway Config: $CURRENT_CONFIG_ID"
echo "Target Gateway Config:  $TARGET_CONFIG_ID"

if [ "$CURRENT_CONFIG_ID" == "$TARGET_CONFIG_ID" ]; then
    echo "Success: Gateway is already serving the target configuration."
    exit 0
else
    echo "Updating Gateway to use $TARGET_CONFIG_ID..."
    gcloud api-gateway gateways update $GATEWAY_ID \
        --api=$API_ID \
        --api-config=$TARGET_CONFIG_ID \
        --location=$REGION \
        --project=$PROJECT_ID
    echo "Gateway update initiated successfully."
fi
