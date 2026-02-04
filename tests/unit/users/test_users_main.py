import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from unittest.mock import MagicMock, patch, AsyncMock


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


@pytest.mark.asyncio
async def test_docs_endpoint(client, users_modules, mock_db_session):
    settings = users_modules.config.get_settings()

    # Basic Auth
    auth = (settings.DOCS_USERNAME, settings.DOCS_PASSWORD)

    # Mock db.execute for user check
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None  # User not found
    mock_db_session.execute.return_value = mock_result

    with patch("main.create_user_with_password", new_callable=AsyncMock) as mock_create:
        response = await client.get("/docs", auth=auth)
        assert response.status_code == 200
        assert "swagger-ui" in response.text
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_docs_endpoint_existing_user(
    client, users_modules, mock_db_session, mock_user
):
    settings = users_modules.config.get_settings()

    auth = (settings.DOCS_USERNAME, settings.DOCS_PASSWORD)

    # Mock db.execute for user check
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user  # User found
    mock_db_session.execute.return_value = mock_result

    with patch("main.create_user_with_password", new_callable=AsyncMock) as mock_create:
        response = await client.get("/docs", auth=auth)
        assert response.status_code == 200
        mock_create.assert_not_called()


@pytest.mark.asyncio
async def test_lifespan(users_modules):
    main = users_modules.main

    # Mock engine
    with patch("main.engine") as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn

        async with main.lifespan(main.app):
            pass

        mock_conn.run_sync.assert_called_once()
