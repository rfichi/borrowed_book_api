# Decision Rules & Frameworks

**Version:** 1.0.0  
**Last Updated:** 2026-01-30  
**Status:** Active  

## Overview
This document defines the explicit decision-making frameworks and criteria for the Borrowed Book API project. These rules serve as guardrails for the TRAE assistant to ensure consistency, reliability, and alignment with the project's architectural goals.

## Core Decision Principles

### 1. Architectural Consistency
- **Rule:** All new feature implementations must adhere to the microservices architecture.
- **Criterion:** Do not add business logic to the root-level `routers/` or `services/` (monolith remnants) unless explicitly migrating them to `services/{domain}/`.
- **Trigger:** When asked to add a new entity or endpoint, verify which microservice it belongs to (`users`, `books`, `borrow`).

### 2. Cloud-Native First
- **Rule:** Design for Google Cloud Run (Serverless/Stateless).
- **Criterion:**
  - No local file system persistence for application state.
  - Use environment variables for configuration (secrets via Secret Manager).
  - Logs must be structured (JSON) for Cloud Logging.

### 3. Security by Default
- **Rule:** All public API endpoints must be protected.
- **Criterion:**
  - Swagger UI: Basic Auth (admin/admin for POC).
  - API Endpoints: JWT Bearer Token.
- **Constraint:** Do not hardcode secrets in source code.

### 4. Git Branching Strategy
- **Rule:** Use the designated feature branch.
- **Current Branch:** `feature/separate_concerns_borrow_service`
- **Criterion:**
  - Do not commit to `main` directly.
  - **Creating a New Branch Workflow:**
    1. If any changes on current branch, stash them: `git stash -u` (include untracked files).
    2. Checkout to main: `git checkout main`
    3. Update main: `git pull origin main`
    4. Create new branch from updated main: `git checkout -b feature/{feature_name}`
    5. Apply stashed changes (if any): `git stash apply`
  - Branch names should follow the format `feature/{feature_name}`.
  - After pushing feature branch to remote, create a pull request, target `main`.
  - All pull requests must be reviewed and approved by at least one team member.
  - Once approved, merge into `main` using a squash merge.

## Decision Matrix

| Scenario | Decision Path | Rationale |
| :--- | :--- | :--- |
| **New Endpoint Needed** | 1. Identify Domain (User/Book/Borrow)<br>2. Add to `services/{domain}/routers.py`<br>3. Update `api_gateway_config.yaml` | Keeps services decoupled and gateway updated. |
| **Database Schema Change** | 1. Update `models.py` in service<br>2. Update `schemas.py`<br>3. (Future) Create Alembic migration | Ensures DB consistency (currently manual sync for POC). |
| **External Service Call** | 1. Use Asynchronous HTTP client (httpx)<br>2. Implement retries | Cloud Run scales to zero; sync calls block. |
| **Configuration Change** | 1. Update `config.py` using Pydantic BaseSettings<br>2. Update `Dockerfile` ENV (or deployment script) | 12-factor app compliance. |

## Cross-References
- [Coding Conventions](coding-conventions.md)
- [Architectural Patterns](architectural-patterns.md)
