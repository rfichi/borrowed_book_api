$ErrorActionPreference = "Stop"

$PROJECT_ID = "teak-strength-485420-v3"
$SHORT_SHA = $(git rev-parse --short HEAD)
$REGION = "us-central1"
$REPO_BASE = "us-central1-docker.pkg.dev/$PROJECT_ID/borrow-api-repo"
$SA_EMAIL = "ai-assistant-cloud-run-sa@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "Configuring Docker authentication..."
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# --- SHARED BUILDER ---
Write-Host "`n[Builder] Building..."
docker build -t "$REPO_BASE/builder:latest" -f Dockerfile.builder .
Write-Host "[Builder] Pushing..."
docker push "$REPO_BASE/builder:latest"

# --- USERS SERVICE ---
Write-Host "`n[Users Service] Building..."
docker build -t "$REPO_BASE/users-service:$SHORT_SHA" -t "$REPO_BASE/users-service:latest" --build-arg "BUILDER_IMAGE=$REPO_BASE/builder:latest" services/users
Write-Host "[Users Service] Pushing..."
docker push "$REPO_BASE/users-service:$SHORT_SHA"
docker push "$REPO_BASE/users-service:latest"
Write-Host "[Users Service] Deploying..."
gcloud run deploy users-service --image "$REPO_BASE/users-service:$SHORT_SHA" --region $REGION --platform managed --allow-unauthenticated --service-account $SA_EMAIL

# --- BOOKS SERVICE ---
Write-Host "`n[Books Service] Building..."
docker build -t "$REPO_BASE/books-service:$SHORT_SHA" -t "$REPO_BASE/books-service:latest" --build-arg "BUILDER_IMAGE=$REPO_BASE/builder:latest" services/books
Write-Host "[Books Service] Pushing..."
docker push "$REPO_BASE/books-service:$SHORT_SHA"
docker push "$REPO_BASE/books-service:latest"
Write-Host "[Books Service] Deploying..."
gcloud run deploy books-service --image "$REPO_BASE/books-service:$SHORT_SHA" --region $REGION --platform managed --allow-unauthenticated --service-account $SA_EMAIL

# --- BORROW SERVICE ---
Write-Host "`n[Borrow Service] Building..."
docker build -t "$REPO_BASE/borrow-service:$SHORT_SHA" -t "$REPO_BASE/borrow-service:latest" --build-arg "BUILDER_IMAGE=$REPO_BASE/builder:latest" services/borrow
Write-Host "[Borrow Service] Pushing..."
docker push "$REPO_BASE/borrow-service:$SHORT_SHA"
docker push "$REPO_BASE/borrow-service:latest"
Write-Host "[Borrow Service] Deploying..."
gcloud run deploy borrow-service --image "$REPO_BASE/borrow-service:$SHORT_SHA" --region $REGION --platform managed --allow-unauthenticated --service-account $SA_EMAIL

Write-Host "`nManual deployment completed successfully."
