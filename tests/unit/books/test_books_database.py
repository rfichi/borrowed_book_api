import pytest
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_get_db(books_modules):
    database = books_modules.database

    # Mock AsyncSessionLocal to return a mock session
    mock_session = AsyncMock()
    mock_session.close = AsyncMock()

    # We need to mock the context manager behavior of AsyncSessionLocal()
    # AsyncSessionLocal() returns a session object (or context manager)
    # When we do `async with AsyncSessionLocal() as session:`

    mock_session_class = MagicMock()
    mock_session_class.return_value.__aenter__.return_value = mock_session
    mock_session_class.return_value.__aexit__.return_value = None

    with patch.object(database, "AsyncSessionLocal", mock_session_class):
        gen = database.get_db()
        session = await anext(gen)
        assert session == mock_session

        try:
            await anext(gen)
        except StopAsyncIteration:
            pass

        mock_session.close.assert_called_once()


def test_postgres_url_replacement(books_modules):
    # We need to reload the module with mocked settings to test this
    import sys
    from importlib import reload

    with patch("config.get_settings") as mock_settings:
        mock_settings.return_value.DATABASE_URL = "postgresql://user:pass@localhost/db"

        # Reload database module
        if "database" in sys.modules:
            reload(sys.modules["database"])

        from database import SQLALCHEMY_DATABASE_URL

        assert "postgresql+asyncpg://" in SQLALCHEMY_DATABASE_URL


def test_sqlite_url_replacement(books_modules):
    import sys
    from importlib import reload

    with patch("config.get_settings") as mock_settings:
        mock_settings.return_value.DATABASE_URL = "sqlite:///test.db"

        if "database" in sys.modules:
            reload(sys.modules["database"])

        from database import SQLALCHEMY_DATABASE_URL

        assert "sqlite+aiosqlite:///" in SQLALCHEMY_DATABASE_URL
