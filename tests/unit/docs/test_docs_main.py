import pytest
from fastapi.security import HTTPBasicCredentials


def test_root_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Docs Service"}


def test_docs_auth_failure_no_credentials(client):
    """Test accessing /docs without credentials."""
    response = client.get("/docs")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_docs_auth_failure_wrong_credentials(client):
    """Test accessing /docs with wrong credentials."""
    response = client.get("/docs", auth=("wrong", "wrong"))
    assert response.status_code == 401


def test_docs_auth_success(client):
    """Test accessing /docs with correct credentials."""
    # Using admin:admin as hardcoded in the service
    response = client.get("/docs", auth=("admin", "admin"))
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for key content in the custom HTML
    assert "<title>Borrowed Book API Docs</title>" in response.text
    assert "SwaggerUIBundle" in response.text
    assert "urls" in response.text
    assert "/users/openapi.json" in response.text


def test_docs_auth_function(docs_modules):
    """Unit test for the get_current_username dependency function."""
    main = docs_modules.main
    from fastapi import HTTPException

    # Valid credentials
    creds = HTTPBasicCredentials(username="admin", password="admin")
    username = main.get_current_username(creds)
    assert username == "admin"

    # Invalid credentials
    invalid_creds = HTTPBasicCredentials(username="admin", password="wrong")
    with pytest.raises(HTTPException) as exc:
        main.get_current_username(invalid_creds)
    assert exc.value.status_code == 401
