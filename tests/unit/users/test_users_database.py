import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_get_db(users_modules):
    database = users_modules.database

    with patch("database.AsyncSessionLocal") as mock_session_maker:
        mock_session = AsyncMock()
        # Configure context manager to return the session itself
        mock_session.__aenter__.return_value = mock_session
        mock_session_maker.return_value = mock_session

        gen = database.get_db()
        session = await anext(gen)
        assert session == mock_session

        try:
            await anext(gen)
        except StopAsyncIteration:
            pass

        mock_session.close.assert_called_once()


def test_postgres_url_replacement(users_modules):
    import sys
    from importlib import reload

    with patch("config.get_settings") as mock_settings:
        mock_settings.return_value.DATABASE_URL = "postgresql://user:pass@localhost/db"

        if "database" in sys.modules:
            reload(sys.modules["database"])

        from database import SQLALCHEMY_DATABASE_URL

        assert "postgresql+asyncpg" in SQLALCHEMY_DATABASE_URL


def test_sqlite_url_replacement(users_modules):
    import sys
    from importlib import reload

    with patch("config.get_settings") as mock_settings:
        mock_settings.return_value.DATABASE_URL = "sqlite:///test.db"

        if "database" in sys.modules:
            reload(sys.modules["database"])

        from database import SQLALCHEMY_DATABASE_URL

        assert "sqlite+aiosqlite" in SQLALCHEMY_DATABASE_URL
