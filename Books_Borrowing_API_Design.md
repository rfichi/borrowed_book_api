# 📘 Books Borrowing API  
### One-Page Technical Design Document

---

## 1. Purpose & Scope

### Objective
Build a RESTful API that manages **books, users, and borrowing books** for a library-style system.

The API enables:
- Creating and retrieving books
- Creating and retrieving users
- Borrowing and returning books
- Tracking borrowing history per user

### Out of Scope (v1)
- Authentication / Authorization
- Notifications
- Distributed systems / multi-region support

---

## 2. Core Design Principles

- RESTful resource-oriented API  
- Clear separation of concerns  
- Explicit data contracts  
- Dependency injection  
- Testable, maintainable architecture  
- Minimal assumptions, scalable by design  

---

## 3. Core Technology Stack

| Layer | Technology |
|-----|-----------|
| API Framework | FastAPI |
| Data Validation | Pydantic |
| ORM | SQLAlchemy |
| Database | SQLite3 |
| Server | Uvicorn |
| Configuration | python-dotenv |
| Migrations (optional) | Alembic |

SQLite is used for simplicity and local development.  
The system must allow switching to PostgreSQL or MySQL via configuration only.

---

## 4. Configuration Strategy

- Database configuration must be centralized  
- SQLite3 must be used as the default database engine  
- The database connection string must be configurable via environment variables  
- No hardcoded infrastructure logic should exist in business code  

---

## 5. High-Level Architecture

The system is divided into **six layers**, each with a single responsibility.

---

### 5.1 Application Layer (main.py)

**Responsibility**
- Application bootstrap
- Router registration
- Database initialization

**Constraints**
- No business logic
- No database queries

---

### 5.2 Configuration Layer (config.py)

**Responsibility**
- Load environment variables
- Expose runtime settings (e.g. database URL)

**Key Rule**
- Configuration must be injectable and environment-driven

---

### 5.3 Persistence Layer (database.py, models)

**Responsibility**
- Database engine and session lifecycle
- ORM models defining tables and relationships

**Models**
- User: represents system users  
- Book: represents books and availability state  
- BorrowRecord: junction table tracking borrow and return history  

**Constraints**
- No request validation  
- No HTTP concerns  

---

### 5.4 Schema Layer (schemas)

**Responsibility**
- Define API input and output contracts
- Enforce validation rules

**Key Rule**
- ORM models and API schemas must remain independent

---

### 5.5 Transport Layer (routers)

**Responsibility**
- Handle HTTP requests
- Validate input via schemas
- Delegate logic to services

**Routers**
- /books  
- /users  
- /books/{id}/borrow  

**Constraints**
- No business rules  
- Minimal logic  

---

### 5.6 Business Logic Layer (services)

**Responsibility**
- Enforce domain rules

**Examples**
- A book cannot be borrowed twice  
- Borrowing creates a historical record  
- Returning a book updates availability and timestamps  

---

## 6. API Resource Model (Conceptual)

User  
└── BorrowRecord  
  └── Book  

---

## 7. REST Conventions

- Use nouns, not verbs  
- Use HTTP methods for intent  
- Use proper status codes  

---

## 8. Expected Outcomes

This design ensures:
- Clear ownership of responsibilities  
- Easy onboarding for new engineers or AI agents  
- Safe evolution of the system  
- Production readiness without overengineering  

---

## 9. Summary

This API is simple by default, explicit in behavior, scalable in structure, and designed to evolve.

---

## 10. Staff-Level Takeaway

This design allows the system to start simple with SQLite while keeping the door open for future growth without rewriting core logic.

## 11. Q&A

**How will the system handle concurrent requests?**  
SQLite is not designed for high concurrency. In production, PostgreSQL or MySQL should be used.

**Is it possible to switch the database engine without code changes?**  
Yes, the database connection string is configurable.

**How will the system handle book availability?**  
The system tracks book availability using the `Book` model.

**How will the system handle user borrowing history?**  
The system tracks borrowing history using the `BorrowRecord` model.

**You’re designing a REST API for books. What should the endpoint be for borrowing a book with ID 5?**
http://demo.api/books/5/borrow/

**If a client tries to borrow a book that’s already borrowed, what HTTP status code should you return and why?**
status code 403 since the books was already borrowed.

**How would you model the difference between input (creating a book) and output (returning a book with ID) in FastAPI?**
Defining 2 different models, one is the base book models for adding the id and the other one BookCreate that extends from the base book model.

**What’s wrong with having an endpoint like /getBooks instead of /books?**
is semantically incorrect, we should always use nouns and not verbs/actions.

**A user calls DELETE /books/5. The book exists and is removed successfully. What’s the correct HTTP status code to return?**
The status code should be 204, it was a successfull response but no result should be returned.

**In FastAPI, how would you validate that a book’s published_year is not in the future?**
By using Pyndatic.Field(), allowing to specify any date start and limit.

**Your API should return all borrow records for user with ID 10. What should the endpoint look like?**
http://demo.api/users/10/borrow-history/

## 12. Endpoints Examples:
- Add a book (title, author, published_year)
endpoint: http://demo.api/books/
method: POST
body: {"title": "name1", "author": "Juan", "published_year": 2005}
result: {"id": 1, title": "name1", "author": "Juan", "published_year": 2005}
status: [201, 202, 400, 403, 404, 500]

- Get a book by ID
endpoint: http://demo.api/books/1
method: GET
results: {"id": 1, title": "name1", "author": "Juan", "published_year": 2005} or {}
status: [200, 204, 403, 404, 500]

- List all books
endpoint: http://demo.api/books
method: GET
results: {"page": 1, "page_size": 20, "total": 1, "results": [{"id": 1, title": "name1", "author": "Juan", "published_year": 2005}]}
status: [200, 403, 404, 500]


- Delete a book by ID
endpoint: http://demo.api/books/1
method: DELETE
results: {}
status: [204, 403, 404, 500]