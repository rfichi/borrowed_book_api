# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.5] - 2026-02-03

### Added
- Expanded unit test coverage for `borrow`, `books`, and `users` services to achieve >90% coverage.
- Added `diff-cover` to pre-commit hooks to enforce 90% coverage on new lines.

### Changed
- Updated `ci-tests.yaml` to fail if test coverage is below 90%.
- Updated `pre-commit-config.yaml` to include XML coverage generation.

## [0.5.4] - 2026-02-03

### Added
- Created `tests/e2e` directory with `pytest` based E2E tests (`test_user_flow.py`).
- Created `tests/unit` and `tests/integration` directories for better test organization.
- Registered `e2e` marker in `pyproject.toml`.

### Changed
- Refactored project structure: Moved existing unit tests to `tests/unit/`.
- Updated `cloudbuild.yaml` to run `pytest tests/e2e` instead of `verify_gateway.py` script.
- Updated `conftest.py` files to reflect new directory depth.
- Updated Agent Skills documentation to enforce strict git workflow rules (no command chaining, append-only changelog).
- Fixed `ci-tests.yaml` triggers: Added `push` to `main` and `workflow_dispatch` to ensure pipeline stability.

## [0.5.3] - 2026-02-02

### Added
- Integrated E2E smoke tests into Cloud Build pipeline.
- Added `demo/verify_gateway.py` execution as a post-deployment verification step.
- Configured Secret Manager integration for API Key injection in CI/CD.

## [0.5.2] - 2026-02-02

### Changed
- Updated CI/CD pipeline to trigger only on pull requests to main, removing push triggers.

## [0.5.1] - 2026-02-02

### Changed
- Manually Updated `setup.py` and `pyproject.toml` version to `0.5.1`.
- Updated GitHub Actions to enforce >60% test coverage.
- Changelog format updated to match the new structure.

### Fixed
- Restored CHANGELOG.md old entries that were removed.

## [0.5.0] - 2026-02-02

### Added
- Added CI/CD pipeline for automated testing with pytest and coverage.
- Added pytest and pytest-cov dependencies to all services.
- Configured GitHub Actions to enforce >70% test coverage.

## [0.4.4] - 2026-02-02

### Added
- Optimized Dockerfiles using multi-stage builds.
- Updated Cloud Build pipeline to use caching and parallel builds.
- Reduced build time and image size.

## [0.4.3] - 2026-02-02

### Added
- Removed legacy root-level `models/`, `schemas/`, and `routers/` folders.
- Decoupled services to use their own internal dependencies.
- Added MIT License.

## [0.4.2] - 2026-02-01

### Added
- **Test Infrastructure**: Implemented module-scoped fixture pattern (`[service]_modules`) in `conftest.py` for `users`, `books`, and `borrow` services.
- **Isolation**: Enforced strict `sys.path` management with post-test cleanup to prevent cross-service module pollution.
- **Refactoring**: Updated all unit tests to inject service modules via fixtures instead of relying on global imports.

### Fixed
- Fixed `pytest tests/` execution failures caused by module name collisions (e.g., `service.py` from different services).
- Resolved `ImportError` and `AttributeError` issues in the test suite.
- Eliminated the need for dangerous pre-commit hooks or separate test runs.

## [0.4.1] - 2026-02-01

### Added
- **Service Isolation**: Refactored `borrow`, `books`, and `users` services to enforce strict isolation.
  - Replaced absolute imports (e.g., `services.borrow.*`, `services.books.*`, `services.users.*`) with local imports in all services.
  - Verified `Dockerfile` for all services to align with the isolated structure.
  - Updated unit tests (`tests/borrow`, `tests/books`, `tests/users`) to support local service execution and imports.

### Fixed
- Resolved `ModuleNotFoundError` when running services locally in isolation.
- Fixed `ImportError` in unit tests caused by import path mismatches.
- Resolved Cloud Run deployment issues caused by container startup failures due to import errors.

## [0.4.0] - 2026-02-01

### Added
- **CI/CD**: Added `cloudbuild.yaml` configuration for Google Cloud Build.
  - Automates building Docker images for `users`, `books`, and `borrow` services.
  - Automates pushing images to Artifact Registry.
  - Automates deployment to Cloud Run upon push to `main` branch.
- **Documentation**: Added `docs/deployment.md` detailing the setup and verification process for the Cloud Build trigger.
- **Fixes**: Updated `cloudbuild.yaml` to explicitly use `ai-assistant-cloud-run-sa` for Cloud Run deployments to resolve `iam.serviceaccounts.actAs` permission errors.

## [0.3.2] - 2026-02-01

### Added
- **Standardization**: Replaced `requests` and `FastAPI TestClient` with `httpx` and `httpx.AsyncClient` across all services (`users`, `books`, and `borrow`).
- **Testing**: Migrated all unit tests to asynchronous tests using `pytest-anyio` to align with the new async HTTP client pattern.
- **Dependencies**: Added `httpx` dependency to the `users` service.

## [0.3.1] - 2026-02-01

### Added

- **Git Workflow**: Updated triggers for branching, committing, and pushing to be explicit user requests rather than task-status dependent.
  - **Documentation**: Enforced strict changelog updates in `SKILL.md`.

## [0.3.0] - 2026-01-30

### Added

- **Service Decoupling**: Refactored `borrow-service` to remove direct database dependencies on `books` and `users` tables.
- **Books Service**: Added `PATCH /books/{id}/availability` endpoint to allow remote availability updates.
- **Borrow Service**: Implemented HTTP client to communicate with `books-service` for status updates, replacing direct DB writes.

## [0.2.0] - 2026-01-29

### Added
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

### Fixed
- Fixed `401 Unauthorized` errors during inter-service communication by implementing Internal API Key headers.
- Resolved separation of concerns violations where services were accessing each other's database tables directly.

## [0.1.0] - Initial Release

### Added
- Initial proof of concept.
- Monolithic FastAPI application.
- Local SQLite database.
- Basic CRUD operations for Users, Books, and Borrow records.
