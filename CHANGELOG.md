# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-01-30

### Status: Service Decoupling

### 🚀 Major Changes

*   **Service Decoupling**: Refactored `borrow-service` to remove direct database dependencies on `books` and `users` tables.
*   **Books Service**: Added `PATCH /books/{id}/availability` endpoint to allow remote availability updates.
*   **Borrow Service**: Implemented HTTP client to communicate with `books-service` for status updates, replacing direct DB writes.

## [0.2.0] - 2026-01-29

### Status: Live on GCP

### 🚀 Major Changes

*   **Microservices Architecture**: Split the original monolithic application into three distinct services: `users`, `books`, and `borrow`.
*   **Cloud Migration**: Fully migrated infrastructure to Google Cloud Platform.
    *   **Compute**: Services deployed to Cloud Run.
    *   **Database**: Migrated from local SQLite to Google Cloud SQL (PostgreSQL).
*   **Security**:
    *   Implemented JWT authentication for user endpoints.
    *   Added `x-internal-api-key` based authentication for secure inter-service communication.
*   **API Gateway**: Integrated Google API Gateway to route traffic to appropriate Cloud Run services.

### ✨ Features & Improvements

*   **Borrow Service**:
    *   Refactored `borrow_book` and `return_book` logic to validate users and books via external API calls.
    *   Added robust error handling and logging for inter-service requests.
    *   Enforced separation of concerns: Borrow service no longer directly queries User/Book tables for validation (pending full refactor).
*   **Books Service**:
    *   Added endpoints for managing book availability status.
    *   Secured sensitive endpoints.
*   **Users Service**:
    *   Enhanced user retrieval with internal API key support.

### 🐛 Bug Fixes

*   Fixed `401 Unauthorized` errors during inter-service communication by implementing Internal API Key headers.
*   Resolved separation of concerns violations where services were accessing each other's database tables directly.

## [0.1.0] - Initial Release

*   Initial proof of concept.
*   Monolithic FastAPI application.
*   Local SQLite database.
*   Basic CRUD operations for Users, Books, and Borrow records.
