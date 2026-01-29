# Borrowed Book System

A FastAPI service to manage books, users, and borrowing with JWT-based authentication. Designed for local development with SQLite and clean separation of concerns.

## Stack
- FastAPI, Starlette
- Pydantic v2
- SQLAlchemy
- SQLite (default), configurable via DATABASE_URL
- Uvicorn
- JWT (python-jose), password hashing (passlib)
- python-dotenv

## Quick Start

### Windows (PowerShell)
- Create venv:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

- Install deps:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Run:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Linux/macOS
- Create venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Install deps:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Run:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Configuration
- Create a `.env` file (optional):

```
DATABASE_URL=sqlite:///borrowed_books.db
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Authentication
- Signup:

```bash
curl -X POST "http://127.0.0.1:8000/auth/signup?name=Alice&email=alice@example.com&password=secret123"
```

- Login (OAuth2 password):

```bash
curl -X POST "http://127.0.0.1:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=alice@example.com&password=secret123"
```

- Use token:

```bash
TOKEN="paste_token_here"
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/auth/me
```

## Endpoints Examples
- Create book:

```bash
curl -X POST "http://127.0.0.1:8000/books/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Dune","author":"Frank Herbert","published_year":1965}'
```

- List books:

```bash
curl "http://127.0.0.1:8000/books?page=1&page_size=20"
```

- Borrow book:

```bash
curl -X POST "http://127.0.0.1:8000/books/1/borrow" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1}'
```

- Return book:

```bash
curl -X POST "http://127.0.0.1:8000/books/1/return" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1}'
```

## Notes
- This service creates a local SQLite file by default: `borrowed_books.db`.
- For production, set `DATABASE_URL` to PostgreSQL or MySQL.
- API docs: http://127.0.0.1:8000/docs
