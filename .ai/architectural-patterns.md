# Architectural Patterns

**Version:** 1.0.0  
**Last Updated:** 2026-01-30  
**Tags:** #architecture #microservices #gcp #gateway

## System Overview
The Borrowed Book API is a cloud-native application deployed on Google Cloud Platform (GCP). It follows a microservices architecture pattern, orchestrated by a Google Cloud API Gateway.

## Core Components

### 1. API Gateway (`borrow-gateway`)
- **Role:** Entry point for all external traffic.
- **Tech:** Google Cloud API Gateway (OpenAPI 2.0 Spec).
- **Configuration:** `api_gateway_config.yaml`
- **Routing:** Uses `x-google-backend` to route to Cloud Run services.
- **Security:** Handles JWT validation (planned) and routing.

### 2. Microservices (Cloud Run)
Stateless containers running FastAPI applications.
- **Users Service:** Identity, Authentication, User Management.
- **Books Service:** Catalog Management (CRUD).
- **Borrow Service:** Transaction Logic (Borrow/Return).

### 3. Data Persistence
- **Database:** PostgreSQL (Cloud SQL).
- **Pattern:** Shared Database instance (for POC), but logically separated tables.
  - *Future:* Separate databases per service.

## Design Patterns

### Service-to-Service Communication
- **Current (POC):** Synchronous HTTP (REST).
- **Target:** Event-Driven (Pub/Sub) for decoupling (e.g., "Book Borrowed" event updates availability).

### Authentication Flow
1. User logs in via `users-service`.
2. Receives JWT.
3. Client sends JWT in Header to API Gateway.
4. Gateway/Service validates JWT.

### Deployment Pattern
- **Containerization:** Docker.
- **Orchestration:** Cloud Run (Managed Knative).
- **CI/CD:** Cloud Build (planned).

## Diagrams
*(Refer to `docs/books_borrowing_api_design.md` for visual representations)*
