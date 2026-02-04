import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from unittest.mock import patch, MagicMock, AsyncMock


def test_docs_auth_success(borrow_modules):
    main = borrow_modules.main
    config = borrow_modules.config
    settings = config.get_settings()

    credentials = HTTPBasicCredentials(
        username=settings.DOCS_USERNAME, password=settings.DOCS_PASSWORD
    )
    result = main.docs_auth(credentials)
    assert result == credentials


def test_docs_auth_failure(borrow_modules):
    main = borrow_modules.main

    credentials = HTTPBasicCredentials(username="wrong", password="wrong")
    with pytest.raises(HTTPException) as exc:
        main.docs_auth(credentials)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_custom_openapi(borrow_modules):
    main = borrow_modules.main

    # Reset openapi_schema to None to force regeneration
    main.app.openapi_schema = None

    schema = main.custom_openapi()
    assert schema["info"]["title"] == "Borrowed Book System - Borrow Service"
    assert "securitySchemes" not in schema.get("components", {})

    # Check that security requirements are removed from paths
    for path in schema["paths"].values():
        for operation in path.values():
            assert "security" not in operation


@pytest.mark.asyncio
async def test_ensure_docs_user_created(borrow_modules, mock_db_session):
    main = borrow_modules.main

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    email = "test@docs.com"
    password = "password"

    await main.ensure_docs_user(mock_db_session, email, password)

    assert mock_db_session.add.call_count == 2
    assert mock_db_session.commit.call_count == 2
    assert mock_db_session.refresh.call_count == 1


@pytest.mark.asyncio
async def test_ensure_docs_user_exists(borrow_modules, mock_db_session):
    main = borrow_modules.main

    mock_account = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_account
    mock_db_session.execute.return_value = mock_result

    email = "test@docs.com"
    password = "password"

    await main.ensure_docs_user(mock_db_session, email, password)

    mock_db_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_lifespan_coverage(borrow_modules):
    main = borrow_modules.main

    with patch("main.engine") as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_engine.dispose = AsyncMock()

        async with main.lifespan(main.app):
            pass

        mock_conn.run_sync.assert_called_once()
        mock_engine.dispose.assert_called_once()
