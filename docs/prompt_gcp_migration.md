# GCP Migration Plan & Status

## 1. Branch Policy
- ✅ Every new change should be on a new branch called `feature/deliver_borrow_api_on_gcp`.

## 2. Prerequisites
- ✅ gcloud CLI installed and authenticated.
- ✅ Docker client configured.
- ✅ Environment variables path updated.

## 3. Implementation Checklist

### GCP Project Setup
- ✅ Create a new GCP project and set it active.
  - Project ID: `teak-strength-485420-v3`
- ✅ Attach billing and confirm free credits availability.
- ✅ Enable APIs: Cloud Run, Artifact Registry, Cloud Build, Cloud SQL Admin, IAM.
- ✅ Install and authenticate gcloud CLI; configure project and region (us-central1).
- ✅ Create an Artifact Registry (Docker) repo; configure Docker credential helper for gcloud.
  - Repo: `us-central1-docker.pkg.dev/teak-strength-485420-v3/borrow-repo`

### Database Configuration
- ✅ Decide on primary DB: Cloud SQL Postgres (PostgreSQL 18, db-f1-micro).
- ✅ Fallback strategy agreed (VM with Docker).
- ✅ Create the instance, database, and application user/password.
  - Instance Name: `free-borrow-instance-db`
  - DB Name: `borrow-db`
  - Schema: `borrow_schema`
  - User: `borrow_user`
- ✅ Note INSTANCE_CONNECTION_NAME: `teak-strength-485420-v3:us-central1:free-borrow-instance-db`

### Microservices Structure
- ✅ Choose microservice names and structure (`services/users`, `services/books`, `services/borrow`).
- ✅ Scaffolding created with Dockerfile and requirements.txt for each service.

### Environment Configuration
- ✅ Provide required environment values:
  - Project ID: `teak-strength-485420-v3`
  - Tags: `environment=dev`
- ✅ DATABASE_URL configured for Cloud SQL.
  - Connection Name: `teak-strength-485420-v3:us-central1:free-borrow-instance-db`
  - Public Connection: Enabled
- ✅ Shared internal API key for inter-service calls.
- ✅ JWT secret and token expiry values set.
- ✅ Confirm public access policy for Cloud Run (POC: allow unauthenticated).
- ✅ Docker images pushed to Artifact Registry.
- ✅ Confirm cost controls (scale-to-zero, no min instances).

### API Gateway (Bonus)
- ✅ Enable services: `apigateway.googleapis.com`, `servicecontrol.googleapis.com`, `servicemanagement.googleapis.com`
- ✅ Create OpenAPI Spec `api_gateway_config.yaml`
- ✅ Create API: `borrow-api`
- ✅ Create API Config: `borrow-config-v1` (iterated to v13)
- ✅ Create Gateway: `borrow-gateway`
- ✅ Gateway URL: `https://borrow-gateway-bwzk395v.uc.gateway.dev`
