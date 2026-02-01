# Deployment Documentation

This document outlines the deployment process for the Borrowed Book API using Google Cloud Build and Cloud Run.

## Overview
We utilize **Google Cloud Build** to automate the build and deployment of our microservices. When code is pushed to the `main` branch, Cloud Build automatically:
1. Builds Docker images for `users`, `books`, and `borrow` services.
2. Pushes these images to the Google Artifact Registry.
3. Deploys the updated services to Google Cloud Run.

## Prerequisites
Before setting up the trigger, ensure you have:
1. A Google Cloud Platform Project.
2. Enabled APIs:
   - Cloud Build API
   - Cloud Run Admin API
   - Artifact Registry API
3. Created an Artifact Registry repository named `borrow-api-repo` in region `us-central1`.

## Setup Instructions

### 1. Connect Repository to Cloud Build
1. Go to the [Cloud Build Triggers page](https://console.cloud.google.com/cloud-build/triggers) in the Google Cloud Console.
2. Click **Manage Repositories**.
3. Select **Connect Repository** and choose **GitHub**.
4. Authenticate with GitHub and select the `borrowed_book_api` repository.

### 2. Create Build Trigger
1. Click **Create Trigger**.
2. **Name**: `deploy-borrowed-book-api`
3. **Event**: Push to a branch.
4. **Source**:
   - Repository: `borrowed_book_api` (GitHub)
   - Branch: `^main$`
5. **Configuration**:
   - Type: Cloud Build configuration file (yaml or json)
   - Location: `cloudbuild.yaml` (Repository)
6. **Service Account**:
   - Select the default Cloud Build Service Account.
   - **Crucial**: Ensure this service account has the `Cloud Run Admin` and `Service Account User` roles.

### 3. Verification
1. Push a change to the `main` branch.
2. Visit the [Cloud Build History page](https://console.cloud.google.com/cloud-build/builds) to watch the build progress.
3. Verify that new revisions are created in Cloud Run for all three services.

## Cost Considerations
- **Cloud Build**: First 120 build-minutes per day are free. Afterward, standard machine types cost approx. $0.003/min.
- **Artifact Registry**: Storage costs apply (approx. $0.10/GB/month).
- **Cloud Run**: You pay for CPU/Memory allocated during request processing.

## Troubleshooting
- **Build Fails**: Check the build logs in Cloud Build Console. Common issues include Dockerfile errors or missing dependencies.
- **Deploy Fails**: Check Cloud Run logs. Ensure the Service Account has permission to deploy.
