# Borrowed Book API (v0.2.0)

A scalable microservices-based application for managing book borrowing, built with FastAPI and deployed on Google Cloud Platform.

## 🚀 Overview

This project has evolved from a monolithic local application to a distributed microservices architecture. It allows users to browse books, manage their profiles, and borrow/return books, with data persistence handled by a centralized PostgreSQL database on Cloud SQL.

## 🏗 Architecture

The system is composed of three decoupled microservices, communicating via REST APIs and secured with JWT and Internal API Keys.

### Microservices
*   **Users Service**: Manages user registration, authentication, and profiles.
*   **Books Service**: Handles the book catalog (CRUD operations) and availability status.
*   **Borrow Service**: Orchestrates borrowing and returning logic, ensuring data consistency across services.

### Infrastructure (GCP)
*   **Compute**: Google Cloud Run (Serverless container deployment).
*   **Database**: Google Cloud SQL (PostgreSQL) shared instance.
*   **Gateway**: Google API Gateway for centralized routing and security.
*   **Registry**: Google Artifact Registry for container images.

## 🛠 Tech Stack

*   **Language**: Python 3.10+
*   **Framework**: FastAPI
*   **Database**: PostgreSQL (SQLAlchemy ORM)
*   **Authentication**: OAuth2 with JWT (User auth) & Internal API Keys (Service-to-Service).
*   **Deployment**: Docker & Google Cloud Platform.

## 📦 Usage

### Prerequisites
*   Google Cloud SDK installed and authenticated.
*   Docker installed.
*   PostgreSQL client (optional for local testing).

### Running Locally (Docker Compose)
*Coming soon...*

### API Documentation
The API is exposed via Google API Gateway. You can access the Swagger UI for individual services (if exposed) or interact via the Gateway URL.

**Base URL**: `https://borrow-gateway-bwzk395v.uc.gateway.dev`

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 👥 Authors

*   **Rusel Fichi**
