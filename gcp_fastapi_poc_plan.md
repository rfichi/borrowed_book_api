# GCP POC Deployment Plan – FastAPI Microservices with PostgreSQL

## Objective
Create a **zero/near-zero cost Proof of Concept (POC)** on **Google Cloud Platform** with:
- 3 Dockerized FastAPI microservices
- PostgreSQL as the primary database (Cloud SQL)
- Fallback to a free VM-based PostgreSQL if credits expire
- Simple, correct, and production-inspired architecture

---

## Technology Stack
- Python >= 3.10
- FastAPI
- PostgreSQL
- Docker
- Ubuntu
- Google Cloud Platform (Cloud Run, Cloud SQL)

---

## High-Level Architecture

```
Client
  |
HTTPS
  |
Cloud Run (Service A, B, C)
  |
Unix Socket / Private Network
  |
Cloud SQL (PostgreSQL)
```

Fallback:
```
Cloud Run -> Compute Engine VM (Postgres via Docker)
```

---

## Phase 1 – Project & Account Setup

### 1. Create GCP Project
- Create a new GCP project dedicated to the POC
- Set it as the active project

### 2. Enable Required APIs
- Cloud Run
- Artifact Registry
- Cloud Build
- Cloud SQL Admin
- IAM

### 3. Configure Billing
- Attach billing account
- Monitor free credits usage

---

## Phase 2 – Repository & Code Structure

### 4. Define Monorepo Structure
- Root repository
- One folder per microservice
- Shared database utilities (optional)

### 5. Define Service Standards
Each microservice must:
- Be independently deployable
- Expose FastAPI app
- Have its own Dockerfile
- Use environment variables for configuration

---

## Phase 3 – Dockerization

### 6. Create Dockerfile per Service
- Base image: python:3.11-slim
- Expose port 8080
- Run via uvicorn

### 7. Local Validation
- Build images locally
- Run containers locally
- Verify endpoints

---

## Phase 4 – Artifact Registry

### 8. Create Artifact Registry Repository
- Docker format
- Single region (e.g. us-central1)

### 9. Authenticate Docker with GCP
- Configure Docker credential helper

### 10. Build & Push Images
- One image per microservice
- Tag with service name

---

## Phase 5 – PostgreSQL (Primary: Cloud SQL)

### 11. Create Cloud SQL PostgreSQL Instance
- PostgreSQL 15
- db-f1-micro tier
- Single region

### 12. Create Database & User
- Create logical database
- Create application user with password

### 13. Connectivity Strategy
- Use Cloud SQL Unix Socket
- No public IP required
- Access controlled via IAM

---

## Phase 6 – Cloud Run Deployment

### 14. Deploy Microservices to Cloud Run
For each service:
- Deploy container image
- Set region
- Allow unauthenticated access (POC)
- Attach Cloud SQL instance
- Configure environment variables

### 15. Environment Variables
- DATABASE_URL (without host)
- INSTANCE_CONNECTION_NAME
- SERVICE_NAME / ENV (optional)

---

## Phase 7 – Database Integration

### 16. SQLAlchemy / AsyncPG Setup
- Use async engine
- Connect via Unix socket
- Shared connection logic pattern

### 17. Schema Management
- Manual SQL or Alembic (optional for POC)

---

## Phase 8 – Inter-Service Communication

### 18. Communication Strategy
- HTTP over Cloud Run public URLs
- Shared internal API key header

### 19. Timeouts & Retries
- Use httpx
- Short timeouts
- Basic retry strategy

---

## Phase 9 – Observability & Debugging

### 20. Logging
- Use standard logging
- View logs in Cloud Logging

### 21. Error Visibility
- Enable FastAPI exception handlers
- Log database connection failures

---

## Phase 10 – Cost Control

### 22. Cloud Run
- Verify scale-to-zero behavior
- Avoid min instances

### 23. Cloud SQL
- Stop instance when idle
- Monitor credit usage

---

## Phase 11 – Fallback Plan (Option B)

### 24. Create Free Compute Engine VM
- f1-micro
- Ubuntu 22.04 LTS
- Always Free eligible region

### 25. Install Docker & PostgreSQL
- Run Postgres via Docker
- Expose private IP only

### 26. Update Cloud Run Configuration
- Switch DATABASE_URL to VM private IP
- Remove Cloud SQL attachment

---

## Phase 12 – Validation & Documentation

### 27. End-to-End Testing
- Validate all service endpoints
- Validate DB access from each service

### 28. Documentation
- Architecture diagram
- Deployment notes
- Known limitations

---

## Out of Scope (POC)
- High availability
- Autoscaling tuning
- Advanced security
- CI/CD pipelines
- Zero-downtime migrations

---

## Expected Outcome
- Fully functional microservices POC
- Near-zero monthly cost
- Realistic cloud-native architecture
- Easy transition to production setup

---

## Next Possible Extensions
- Cloud Build CI/CD
- Secret Manager
- IAM-only internal services
- Pub/Sub async communication
