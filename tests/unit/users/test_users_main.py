import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials


def test_docs_auth_success(users_modules):
    main = users_modules.main
    config = users_modules.config
    settings = config.get_settings()

    credentials = HTTPBasicCredentials(
        username=settings.DOCS_USERNAME, password=settings.DOCS_PASSWORD
    )
    result = main.docs_auth(credentials)
    assert result == credentials


def test_docs_auth_failure(users_modules):
    main = users_modules.main

    credentials = HTTPBasicCredentials(username="wrong", password="wrong")
    with pytest.raises(HTTPException) as exc:
        main.docs_auth(credentials)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_custom_openapi(users_modules):
    main = users_modules.main

    # Reset openapi_schema to None to force regeneration
    main.app.openapi_schema = None

    schema = main.custom_openapi()
    assert schema["info"]["title"] == "Borrowed Book System - Users Service"
    assert "securitySchemes" not in schema.get("components", {})

    # Check that security requirements are removed from paths
    for path in schema["paths"].values():
        for operation in path.values():
            assert "security" not in operation
