# Changelog

All notable changes to this project will be documented in this file.

## [0.4.2] - 2026-02-01

- Status: Test Suite Isolation
- Changes:
  - **Test Infrastructure**: Implemented module-scoped fixture pattern (`[service]_modules`) in `conftest.py` for `users`, `books`, and `borrow` services.
  - **Isolation**: Enforced strict `sys.path` management with post-test cleanup to prevent cross-service module pollution.
  - **Refactoring**: Updated all unit tests to inject service modules via fixtures instead of relying on global imports.
- Fixes:
  - Fixed `pytest tests/` execution failures caused by module name collisions (e.g., `service.py` from different services).
  - Resolved `ImportError` and `AttributeError` issues in the test suite.
  - Eliminated the need for dangerous pre-commit hooks or separate test runs.
- Breaking Changes

## [0.4.1] - 2026-02-01

- Status: Service Isolation Fixes
- Changes:
  - **Service Isolation**: Refactored `borrow`, `books`, and `users` services to enforce strict isolation.
    - Replaced absolute imports (e.g., `services.borrow.*`, `services.books.*`, `services.users.*`) with local imports in all services.
    - Verified `Dockerfile` for all services to align with the isolated structure.
    - Updated unit tests (`tests/borrow`, `tests/books`, `tests/users`) to support local service execution and imports.
- Fixes:
  - Resolved `ModuleNotFoundError` when running services locally in isolation.
  - Fixed `ImportError` in unit tests caused by import path mismatches.
  - Resolved Cloud Run deployment issues caused by container startup failures due to import errors.
- Breaking Changes

## [0.4.0] - 2026-02-01

- Status: CI/CD Pipeline Setup
- Changes:
  - **CI/CD**: Added `cloudbuild.yaml` configuration for Google Cloud Build.
    - Automates building Docker images for `users`, `books`, and `borrow` services.
    - Automates pushing images to Artifact Registry.
    - Automates deployment to Cloud Run upon push to `main` branch.
  - **Documentation**: Added `docs/deployment.md` detailing the setup and verification process for the Cloud Build trigger.
  - **Fixes**: Updated `cloudbuild.yaml` to explicitly use `ai-assistant-cloud-run-sa` for Cloud Run deployments to resolve `iam.serviceaccounts.actAs` permission errors.
- Fixes:
  - None
- Breaking Changes

## [0.3.2] - 2026-02-01

- Status: Refactoring & Testing Standardization
- Changes:
  - **Standardization**: Replaced `requests` and `FastAPI TestClient` with `httpx` and `httpx.AsyncClient` across all services (`users`, `books`, `borrow`).
  - **Testing**: Migrated all unit tests to asynchronous tests using `pytest-anyio` to align with the new async HTTP client pattern.
  - **Dependencies**: Added `httpx` dependency to the `users` service.
- Fixes:
  - None
- Breaking Changes

## [0.3.1] - 2026-02-01

- Status: Workflow Improvements
- Changes:
  - **Git Workflow**: Updated triggers for branching, committing, and pushing to be explicit user requests rather than task-status dependent.
  - **Documentation**: Enforced strict changelog updates in `SKILL.md`.
- Fixes:
  - None
- Breaking Changes

## [0.3.0] - 2026-01-30

- Status: Service Decoupling
- Changes:
  - **Service Decoupling**: Refactored `borrow-service` to remove direct database dependencies on `books` and `users` tables.
  - **Books Service**: Added `PATCH /books/{id}/availability` endpoint to allow remote availability updates.
  - **Borrow Service**: Implemented HTTP client to communicate with `books-service` for status updates, replacing direct DB writes.
- Fixes:
  - None
- Breaking Changes

## [0.2.0] - 2026-01-29

- Status: Live on GCP
- Changes:
  - **Microservices Architecture**: Split the original monolithic application into three distinct services: `users`, `books`, and `borrow`.
  - **Cloud Migration**: Fully migrated infrastructure to Google Cloud Platform.
    - **Compute**: Services deployed to Cloud Run.
    - **Database**: Migrated from local SQLite to Google Cloud SQL (PostgreSQL).
  - **Security**:
    - **Authentication**: Implemented JWT authentication for user endpoints.
    - **Inter-service**: Added `x-internal-api-key` based authentication for secure inter-service communication.
  - **API Gateway**: Integrated Google API Gateway to route traffic to appropriate Cloud Run services.
  - **Borrow Service**:
    - Refactored `borrow_book` and `return_book` logic to validate users and books via external API calls.
    - Added robust error handling and logging for inter-service requests.
    - Enforced separation of concerns: Borrow service no longer directly queries User/Book tables for validation.
  - **Books Service**:
    - Added endpoints for managing book availability status.
    - Secured sensitive endpoints.
  - **Users Service**:
    - Enhanced user retrieval with internal API key support.
- Fixes:
  - Fixed `401 Unauthorized` errors during inter-service communication by implementing Internal API Key headers.
  - Resolved separation of concerns violations where services were accessing each other's database tables directly.
- Breaking Changes

## [0.1.0] - Initial Release

- Status: Proof of Concept
- Changes:
  - Initial proof of concept.
  - Monolithic FastAPI application.
  - Local SQLite database.
  - Basic CRUD operations for Users, Books, and Borrow records.
- Fixes:
  - None
- Breaking Changes
