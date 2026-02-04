# flake8: noqa
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
import secrets
from database import engine, Base, get_db
from routers import borrow_router
from config import get_settings
from models import AuthAccount
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import AuthAccount
from security import create_access_token
from models import User, AuthAccount
from security import get_password_hash
from contextlib import asynccontextmanager

settings = get_settings()
security_basic = HTTPBasic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Borrowed Book System - Borrow Service",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    redirect_slashes=False,
    lifespan=lifespan,
)

app.include_router(borrow_router)


def docs_auth(
    credentials: HTTPBasicCredentials = Depends(security_basic),
) -> HTTPBasicCredentials:
    correct_username = secrets.compare_digest(
        credentials.username, settings.DOCS_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.DOCS_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="0.1.0",
        description="Borrowed Book System - Borrow Service",
        routes=app.routes,
    )
    if (
        "components" in openapi_schema
        and "securitySchemes" in openapi_schema["components"]
    ):
        del openapi_schema["components"]["securitySchemes"]
    for path in openapi_schema.get("paths", {}):
        for method in list(openapi_schema["paths"][path].keys()):
            op = openapi_schema["paths"][path][method]
            if "security" in op:
                del op["security"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


async def ensure_docs_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(AuthAccount).where(AuthAccount.email == email))
    account = result.scalars().first()
    if not account:
        user = User(name="Docs", email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        account = AuthAccount(
            user_id=user.id, email=email, password_hash=get_password_hash(password)
        )
        db.add(account)
        await db.commit()


@app.get("/docs", include_in_schema=False)
async def docs(
    credentials: HTTPBasicCredentials = Depends(docs_auth),
    db: AsyncSession = Depends(get_db),
):
    email = "docs@example.com"
    await ensure_docs_user(db, email, settings.DOCS_PASSWORD)
    token = create_access_token({"sub": email})
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>{app.title} Docs</title>
    </head>
    <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      const AUTH_TOKEN = "{token}";
      const ui = SwaggerUIBundle({{
        url: '{app.openapi_url}',
        dom_id: '#swagger-ui',
        layout: 'BaseLayout',
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        requestInterceptor: (req) => {{
          const skip = req.url.includes('/openapi.json') || req.url.includes('/auth/token') || req.url.includes('/auth/signup');
          if (!skip) {{
            req.headers['Authorization'] = 'Bearer ' + AUTH_TOKEN;
          }}
          return req;
        }},
      }});
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/openapi.json", include_in_schema=False)
def openapi_json(credentials: HTTPBasicCredentials = Depends(docs_auth)):
    return app.openapi()
