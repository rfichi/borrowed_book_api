# flake8: noqa
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
import secrets
from services.users.database import engine, Base, get_db
from services.users.routers import users_router, auth_router
from services.users.config import get_settings
from sqlalchemy.orm import Session
from services.users.models import AuthAccount
from services.users.service import create_user_with_password
from services.users.security import create_access_token

settings = get_settings()
security_basic = HTTPBasic()

app = FastAPI(
    title="Borrowed Book System - Users Service",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    redirect_slashes=False,
)

Base.metadata.create_all(bind=engine)

app.include_router(users_router)
app.include_router(auth_router)


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
        description="Borrowed Book System - Users Service",
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


@app.get("/docs", include_in_schema=False)
def docs(
    credentials: HTTPBasicCredentials = Depends(docs_auth),
    db: Session = Depends(get_db),
):
    email = "docs@example.com"
    account = db.query(AuthAccount).filter(AuthAccount.email == email).first()
    if not account:
        create_user_with_password(
            db, name="Docs", email=email, password=settings.DOCS_PASSWORD
        )
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
