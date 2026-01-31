---
name: "project-guidelines"
description: "Defines coding standards, naming conventions, and design patterns. Invoke when writing code, refactoring, or reviewing implementation details."
---

# Project Guidelines & Coding Standards

## 1. Naming Conventions
- **Files/Modules:** `snake_case` (e.g., `service.py`, `borrow_record.py`).
- **Functions/Variables:** `snake_case` (e.g., `create_book`, `user_id`).
- **Classes/Types:** `PascalCase` (e.g., `Book`, `UserCreate`).
- **Constants:** `UPPER_CASE` (e.g., `MAX_PAGE_SIZE`).

## 2. Documentation & Typing (Mandatory)
- **Docstrings:** All public functions and classes MUST have docstrings.
  - Format: Explain purpose, `param` (with type), `return`, and `raises`.
- **Type Hinting:** All function arguments and return values MUST be typed.
  - Example: `def get_item(id: int) -> Item | None:`
- **Module Headers:** Top of file must include year and purpose.
  - Example: `"""2026 Module responsible for..."""`

## 3. Design Patterns
- **Service Layer:** Business logic lives in `service.py`.
  - **Do NOT** put business logic in `routers.py`.
  - **Do NOT** put database queries in `routers.py`.
- **Dependency Injection:** Inject dependencies (like `db: Session`) explicitly.
- **DTOs vs ORM:**
  - Use **Pydantic Schemas** (`schemas.py`) for API request/response.
  - Use **SQLAlchemy Models** (`models.py`) for database interaction.
  - Explicitly convert between them in the service layer.

## 4. Error Handling
- **Exceptions:** Use `FastAPI.HTTPException` for client-facing errors.
- **Status Codes:** Use `fastapi.status` constants (e.g., `status.HTTP_404_NOT_FOUND`) instead of raw integers.

## 5. Async vs Sync
- The project currently uses **Synchronous** SQLAlchemy (standard `def`).
- Do not mix `async def` with blocking DB calls unless using an async driver.

## 6. File Formatting & Source Control
- **End of File:** All text files (code, markdown, config) MUST end with a single newline character.
  - **Reason:** Prevents `pre-commit` hook failures (`end-of-file-fixer`) and ensures compatibility with POSIX tools.
- **Trailing Whitespace:** Remove all trailing whitespace from lines.
