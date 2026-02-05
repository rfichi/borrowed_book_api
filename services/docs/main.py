"""
2026 Module responsible for serving the centralized Swagger UI documentation.
Aggregates OpenAPI specifications from microservices and protects access with Basic Auth.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import HTMLResponse
import secrets

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

security = HTTPBasic()


def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    """
    Validate Basic Auth credentials.

    Args:
        credentials (HTTPBasicCredentials): The credentials provided by the user.

    Returns:
        str: The username if authentication is successful.

    Raises:
        HTTPException: If credentials are invalid.
    """
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint for health check.

    Returns:
        dict: A simple message indicating the service is running.
    """
    return {"message": "Docs Service"}


@app.get("/docs", response_class=HTMLResponse)
async def get_documentation(
    username: str = Depends(get_current_username),
) -> HTMLResponse:
    """
    Serve the Swagger UI with multiple specs.

    Args:
        username (str): Authenticated username.

    Returns:
        HTMLResponse: The Swagger UI HTML page.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Borrowed Book API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <style>
        body { margin: 0; padding: 0; }
        @media (prefers-color-scheme: dark) {
            body { background-color: #1b1b1b; color: #c9d1d9; }
            .swagger-ui { color: #c9d1d9; }
            .swagger-ui .info .title, .swagger-ui .info h1, .swagger-ui .info h2,
            .swagger-ui .info h3, .swagger-ui .info h4, .swagger-ui .info h5 { color: #c9d1d9; }
            .swagger-ui .scheme-container { background-color: #0d1117; box-shadow: none;
            border-bottom: 1px solid #30363d; }
            .swagger-ui .opblock-tag { color: #c9d1d9; border-bottom: 1px solid #30363d; }
            .swagger-ui .opblock .opblock-summary-operation-id, .swagger-ui .opblock .opblock-summary-path,
            .swagger-ui .opblock .opblock-summary-path__deprecated { color: #c9d1d9; }
            .swagger-ui .opblock .opblock-summary-description { color: #8b949e; }
            .swagger-ui .opblock-section-header { background-color: #0d1117; }
            .swagger-ui .tab li { color: #c9d1d9; }
            .swagger-ui .model { color: #c9d1d9; }
            .swagger-ui .model-title { color: #c9d1d9; }
            .swagger-ui .prop-type { color: #8b949e; }
            .swagger-ui table thead tr th, .swagger-ui table thead tr td { color: #c9d1d9; }
            .swagger-ui .parameter__name { color: #c9d1d9; }
            .swagger-ui .parameter__type { color: #8b949e; }
            .swagger-ui input[type=text], .swagger-ui textarea,
            .swagger-ui select { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; }
            .swagger-ui .dialog-ux .modal-ux { background-color: #1b1b1b; border: 1px solid #30363d; }
            .swagger-ui .dialog-ux .modal-ux-header { border-bottom: 1px solid #30363d; }
            .swagger-ui .dialog-ux .modal-ux-content { color: #c9d1d9; }
        }
    </style>
    </head>
    <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
    window.onload = async function() {
      const urls = [
        "/users/openapi.json",
        "/books/openapi.json",
        "/borrow/openapi.json"
      ];

      try {
        const specs = await Promise.all(urls.map(url => fetch(url).then(res => res.json())));

        const mergedSpec = {
          openapi: "3.0.2",
          info: {
            title: "Borrowed Book API",
            version: "1.0.0"
          },
          paths: {},
          components: {
            schemas: {},
            securitySchemes: {}
          }
        };

        specs.forEach(spec => {
          if (spec.paths) {
            Object.assign(mergedSpec.paths, spec.paths);
          }
          if (spec.components) {
            if (spec.components.schemas) {
              Object.assign(mergedSpec.components.schemas, spec.components.schemas);
            }
            if (spec.components.securitySchemes) {
              Object.assign(mergedSpec.components.securitySchemes, spec.components.securitySchemes);
            }
          }
        });

        const ui = SwaggerUIBundle({
          spec: mergedSpec,
          dom_id: '#swagger-ui',
          deepLinking: true,
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
          ],
          plugins: [
            SwaggerUIBundle.plugins.DownloadUrl
          ],
          layout: "BaseLayout",
          supportedSubmitMethods: []
        })
        window.ui = ui
      } catch (error) {
        console.error("Failed to load OpenAPI specs:", error);
        document.getElementById("swagger-ui").innerHTML =
            "<h2 style='text-align:center; margin-top:50px; color:red;'>Failed to load API definitions.</h2>";
      }
    }
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
