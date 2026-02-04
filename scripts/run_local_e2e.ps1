param (
    [switch]$alive
)

$ErrorActionPreference = "Stop"

function Test-PortAvailability {
    param (
        [string]$Url
    )
    try {
        $request = [System.Net.WebRequest]::Create($Url)
        $request.Method = "HEAD"
        $request.Timeout = 2000 # 2 seconds
        $response = $request.GetResponse()
        $response.Close()
        return $true
    }
    catch {
        # If we get a 404, the server is UP but the path doesn't exist, which is fine for connectivity check
        if ($_.Exception.Response.StatusCode -eq [System.Net.HttpStatusCode]::NotFound) {
            return $true
        }
        return $false
    }
}

Write-Host "Checking Docker status..."
docker info > $null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker is not running. Please start Docker Desktop."
}

Write-Host "Starting local environment..."
if ($build) {
    Write-Host "Building images as requested..." -ForegroundColor Cyan
    docker-compose up -d --build
}
else {
    Write-Host "Starting with existing images..." -ForegroundColor Cyan
    docker-compose up -d
}

Write-Host "Waiting for services to be ready (up to 60s)..."
$retries = 0
$max_retries = 30 # 30 * 2s = 60s
$gateway_url = "http://localhost:8080/auth" # Checking a known path usually helps

while ($retries -lt $max_retries) {
    Write-Host "." -NoNewline
    # We check if we can connect. HEAD might return 405 Method Not Allowed or 404, but that means it's listening.
    try {
        $test = Invoke-WebRequest -Uri $gateway_url -Method Head -ErrorAction SilentlyContinue
        if ($test.StatusCode -lt 500) {
            Write-Host "`nGateway is up!" -ForegroundColor Green
            break
        }
    }
    catch {
        # Check if it's a connection error or just a server error
        if ($_.Exception.Response -ne $null) {
             $statusCode = $_.Exception.Response.StatusCode
             if ([int]$statusCode -lt 500) {
                 Write-Host "`nGateway is up! (Status: $statusCode)" -ForegroundColor Green
                 break
             }
        }
    }

    Start-Sleep -Seconds 2
    $retries++
}

if ($retries -eq $max_retries) {
    Write-Warning "Timeout waiting for Gateway. Tests might fail."
}

Write-Host "Running E2E tests..."
$env:GATEWAY_URL = "http://localhost:8080"
$env:API_KEY = "dummy-key"

try {
    pytest tests/e2e/test_user_flow.py -v
    if ($LASTEXITCODE -ne 0) {
        throw "Pytest failed with exit code $LASTEXITCODE"
    }
}
catch {
        Write-Host "Tests execution failed!" -ForegroundColor Red
        Write-Host "Fetching logs for debugging..." -ForegroundColor Yellow
        docker-compose logs --tail=50
        $global:LastExitCode = 1
    }
finally {
        if ($alive) {
            Write-Host "Keeping local environment alive as requested..." -ForegroundColor Cyan
        }
        else {
            Write-Host "Stopping local environment..."
            docker-compose down
        }
    }
