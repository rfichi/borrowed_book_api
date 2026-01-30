# Context Memory & Decision Log

**Version:** 1.0.0  
**Last Updated:** 2026-01-30  
**Purpose:** Maintain context across sessions and document the rationale behind key decisions.

## Active Context
- **Current Phase:** POC Delivery on GCP - Service Decoupling.
- **Active Branch:** `feature/separate_concerns_borrow_service`
- **Key Blocker/Focus:** Reliability of inter-service communication.

## Decision Log

| Date | Decision | Rationale | Impact | Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-01-30 | Establish `.ai` directory | Need for persistent context and explicit rules for TRAE model. | Improves reliability and consistency. | ✅ Implemented |
| 2026-01-30 | Use Microservices Structure | Scalability and separation of concerns required for GCP. | Codebase split into `services/`. | ✅ Implemented |
| 2026-01-30 | API Gateway for Routing | Unified entry point for multiple Cloud Run services. | Simplifies client interaction. | ✅ Implemented |
| 2026-01-30 | Decouple Borrow Service | Replaced direct DB queries with inter-service HTTP calls. | Improved separation of concerns. | ✅ Implemented |

## Session History Summary

### Session: Initial Setup (2026-01-30)
- **Goal:** Create documentation framework.
- **Outcome:** Created `.ai/` folder and core MD files.
- **Key Learnings:** Need to ensure TRAE reads these files explicitly.

### Session: Service Decoupling (2026-01-30)
- **Goal:** Improve separation of concerns between Books and Borrow services.
- **Outcome:** 
  - Added `PATCH /books/{id}/availability` to Books service.
  - Refactored Borrow service to use HTTP calls instead of direct DB access for Book/User data.
- **Key Learnings:** Inter-service communication via HTTP works well for POC decoupling.

## Future Considerations
- Migrate shared DB to separate DBs.
- Implement Async/Await fully.
