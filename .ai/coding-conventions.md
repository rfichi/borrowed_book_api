# Coding Conventions

**Version:** 1.0.0  
**Last Updated:** 2026-01-30  
**Tags:** #python #fastapi #pydantic #styleguide

## 1. General Python Standards
- **Style Guide:** Follow PEP 8.
- **Type Hinting:** Mandatory for all function arguments and return values.
  ```python
  def get_user(user_id: int) -> User:
      ...
  ```
- **Docstrings:** All public modules, classes, and functions must have docstrings (Google Style or NumPy Style).
  - Modules: Include year and high-level responsibility.

## 2. FastAPI & Pydantic
- **Request Bodies:** MUST use Pydantic models. Do not use raw dicts.
- **Response Models:** Explicitly define `response_model` in decorators.
  ```python
  @router.post("/users", response_model=UserResponse)
  ```
- **Dependency Injection:** Use `Depends()` for database sessions and authentication.

## 3. Project Structure
- **Imports:** Absolute imports preferred within microservices (e.g., `from services.users.models import User`).
- **File Naming:** Snake_case for Python files (`user_service.py`).
- **Class Naming:** PascalCase (`UserProfile`).

## 4. Error Handling
- Use `HTTPException` with clear status codes and details.
- Do not return 500 errors for client-side issues (validation, not found).

## 5. Testing
- Use `pytest`.
- Test files should mirror the source structure in `tests/`.
- Mock external calls (database, other services).

## 6. Documentation
- Update `docs/` for any architectural changes.
- Checklists in docs should use ✅ for completed items.
