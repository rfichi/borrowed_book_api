from unittest.mock import MagicMock
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session

# Add the service directory to sys.path so imports work
# Current file: tests/books/conftest.py
# Target: services/books
SERVICE_PATH = str(Path(__file__).parents[3] / "services" / "books")

COMMON_MODULES = [
    "main",
    "database",
    "models",
    "schemas",
    "security",
    "service",
    "routers",
    "config",
]


@pytest.fixture(scope="module")
def books_modules():
    """
    Sets up the environment for books service tests.
    Imports modules and returns them.
    Cleans up sys.modules after usage.
    """
    # Setup path
    if SERVICE_PATH not in sys.path:
        sys.path.insert(0, SERVICE_PATH)

    # Import modules
    import main
    import database
    import security
    import service
    import routers
    import models
    import config
    import schemas

    # Yield modules
    class Modules:
        pass

    modules = Modules()
    modules.main = main
    modules.database = database
    modules.security = security
    modules.service = service
    modules.routers = routers
    modules.models = models
    modules.config = config
    modules.schemas = schemas

    yield modules

    # Teardown
    if SERVICE_PATH in sys.path:
        sys.path.remove(SERVICE_PATH)

    for module_name in COMMON_MODULES:
        if module_name in sys.modules:
            del sys.modules[module_name]


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_user():
    """Returns a mock user."""
    # We cannot import User here easily without triggering top-level import
    # So we return a mock object that mimics User
    mock = MagicMock()
    mock.id = 1
    mock.name = "Test User"
    mock.email = "test@example.com"
    return mock


@pytest.fixture
def mock_book():
    """Returns a mock book."""
    mock = MagicMock()
    mock.id = 1
    mock.title = "Test Book"
    mock.author = "Test Author"
    mock.published_year = 2023
    mock.is_available = True
    return mock


@pytest.fixture
async def client(books_modules, mock_db_session, mock_user):
    """
    Returns a TestClient with overridden dependencies.
    """
    app = books_modules.main.app
    get_db = books_modules.database.get_db
    get_current_user = books_modules.security.get_current_user
    get_current_user_or_internal_api_key = (
        books_modules.security.get_current_user_or_internal_api_key
    )

    def override_get_db():
        try:
            yield mock_db_session
        finally:
            pass

    def override_get_current_user():
        return mock_user

    def override_get_current_user_or_api_key():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[
        get_current_user_or_internal_api_key
    ] = override_get_current_user_or_api_key

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()
