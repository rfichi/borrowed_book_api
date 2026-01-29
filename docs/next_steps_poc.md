# High Priority Next Steps for Borrowed Book API POC

## 1. Service Inter-communication & Validation (Synchronous)
**Goal:** Ensure data integrity across services.
- **Current State:** The Borrow service accepts `user_id` and `book_id` without verifying if they exist or if the book is actually available in the Books service.
- **Task:** Implement synchronous HTTP calls (using `httpx`) from Borrow Service to:
    - **Users Service:** Verify user existence.
    - **Books Service:** Verify book existence and check `available` status.
- **Outcome:** Prevents invalid borrows and enforces business rules.

## 2. Event-Driven Architecture (Pub/Sub)
**Goal:** Decouple services and handle side-effects asynchronously.
- **Current State:** Updates happen directly or are missing.
- **Task:** Integrate Google Cloud Pub/Sub.
    - **Topic `borrow-events`:** Publish events when a book is borrowed or returned.
    - **Subscriber (Books Service):** Listen to events to update `available` status (e.g., set `False` on borrow, `True` on return).
    - **Subscriber (Users Service):** Listen to events to update user's borrow history.
- **Outcome:** Services remain loosely coupled; failure in logging history doesn't block the borrowing transaction.

## 3. Asynchronous Code Implementation
**Goal:** Improve performance and scalability.
- **Current State:** Code uses synchronous `def` and blocking DB calls (SQLAlchemy sync engine).
- **Task:**
    - Convert FastAPI endpoints to `async def`.
    - Switch SQLAlchemy to use `AsyncSession` and an async driver (e.g., `asyncpg` for PostgreSQL).
    - Use `httpx.AsyncClient` for inter-service HTTP requests.
- **Outcome:** Better handling of concurrent requests, especially I/O bound operations (DB, Network).

## 4. Distributed Tracing & Observability
**Goal:** Visibility into request lifecycle across microservices.
- **Current State:** Logs are isolated per service. Hard to track a request from Gateway -> Borrow -> Books.
- **Task:** Integrate **Google Cloud Trace** (OpenTelemetry).
    - Propagate trace headers through API Gateway and inter-service calls.
- **Outcome:** Ability to visualize latency bottlenecks and debug errors across the distributed system.

## 5. Security Hardening (Secret Manager)
**Goal:** Remove sensitive data from code/env vars.
- **Current State:** Secrets are in environment variables or code (now improved, but env vars in Cloud Run revision are still static).
- **Task:** Store DB credentials, JWT secrets, and API keys in **Google Secret Manager**.
    - Update Cloud Run services to mount secrets as environment variables or volumes.
- **Outcome:** Enterprise-grade security compliance.

## 6. Automated CI/CD Pipeline
**Goal:** Streamline deployment.
- **Current State:** Manual `gcloud` commands to build and deploy.
- **Task:** Configure **Cloud Build** triggers.
    - On git push to `main` -> Run tests -> Build Docker images -> Deploy to Cloud Run.
- **Outcome:** Faster iteration and reduced human error during deployment.
