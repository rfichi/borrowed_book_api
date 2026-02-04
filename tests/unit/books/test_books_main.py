import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from unittest.mock import MagicMock, patch, AsyncMock


def test_docs_auth_success(books_modules):
    main = books_modules.main
    config = books_modules.config
    settings = config.get_settings()

    credentials = HTTPBasicCredentials(
        username=settings.DOCS_USERNAME, password=settings.DOCS_PASSWORD
    )
    result = main.docs_auth(credentials)
    assert result == credentials


def test_docs_auth_failure(books_modules):
    main = books_modules.main

    credentials = HTTPBasicCredentials(username="wrong", password="wrong")
    with pytest.raises(HTTPException) as exc:
        main.docs_auth(credentials)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_custom_openapi(books_modules):
    main = books_modules.main

    # Reset openapi_schema to None to force regeneration
    main.app.openapi_schema = None

    schema = main.custom_openapi()
    assert schema["info"]["title"] == "Borrowed Book System - Books Service"
    assert "securitySchemes" not in schema.get("components", {})

    # Check that security requirements are removed from paths
    for path in schema["paths"].values():
        for operation in path.values():
            assert "security" not in operation


@pytest.mark.asyncio
async def test_ensure_docs_user_existing(books_modules, mock_db_session):
    main = books_modules.main
    models = books_modules.models

    email = "docs@example.com"
    password = "password"

    # Mock existing account
    mock_account = MagicMock(spec=models.AuthAccount)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_account
    mock_db_session.execute.return_value = mock_result

    await main.ensure_docs_user(mock_db_session, email, password)

    # Should not add anything
    mock_db_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_docs_user_new(books_modules, mock_db_session):
    main = books_modules.main

    email = "docs@example.com"
    password = "password"

    # Mock no existing account
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    await main.ensure_docs_user(mock_db_session, email, password)

    # Should add user and account
    assert mock_db_session.add.call_count == 2
    mock_db_session.commit.assert_called()


@pytest.mark.asyncio
async def test_lifespan_coverage(books_modules):
    main = books_modules.main

    # Mock engine
    with patch("main.engine") as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_engine.dispose = AsyncMock()

        async with main.lifespan(main.app):
            pass

        # Verify startup
        mock_conn.run_sync.assert_called_once()

        # Verify shutdown
        mock_engine.dispose.assert_called_once()
