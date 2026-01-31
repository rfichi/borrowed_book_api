---
name: "borrow-api-guide"
description: "Provides architectural overview, tech stack, and development guidelines for the Borrowed Book API. Invoke for project structure or implementation questions."
---

# Borrowed Book API Guide

## Overview
A scalable microservices-based application for managing book borrowing, built with FastAPI and deployed on Google Cloud Platform (Cloud Run, Cloud SQL, API Gateway).

## Architecture
- **Microservices**:
  - `services/users`: User management & auth.
  - `services/books`: Book catalog.
  - `services/borrow`: Borrowing logic.
- **Infrastructure**:
  - **Gateway**: Google API Gateway (routes to services).
  - **Database**: Shared PostgreSQL instance on Cloud SQL.
  - **Auth**: OAuth2 with JWT (User) & Internal API Keys (Service-to-Service).

## Tech Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Data**: PostgreSQL (SQLAlchemy ORM), Pydantic schemas.

## Project Structure
- `services/<service_name>/`: Source code for each microservice.
  - `main.py`: App entry point.
  - `models.py`: Database models.
  - `schemas.py`: Pydantic models.
  - `routers.py`: API endpoints.
  - `service.py`: Business logic.
- `docs/`: Documentation and design specs.

## Development Guidelines
- **Validation**: MUST use Pydantic models for all requests/responses.
- **Documentation**: All functions MUST have docstrings and type hinting.
- **Conventions**: Follow existing patterns in `services/books` for consistency.
