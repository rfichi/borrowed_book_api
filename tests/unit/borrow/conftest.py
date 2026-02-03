from unittest.mock import MagicMock
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session

# Add the service directory to sys.path so imports work
# Current file: tests/borrow/conftest.py
# Target: services/borrow
SERVICE_PATH = str(Path(__file__).parents[3] / "services" / "borrow")

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
def borrow_modules():
    """
    Sets up the environment for borrow service tests.
    Imports modules and returns them.
    Cleans up sys.modules after usage to prevent pollution.
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

    # Yield modules as a simple object or dict
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

    # Teardown: Remove path and unload modules
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
    """Returns a mock user (as a dict/object expected by security)."""
    mock = MagicMock()
    mock.id = 1
    mock.email = "test@example.com"
    return mock


@pytest.fixture
async def client(borrow_modules, mock_db_session, mock_user):
    """
    Returns a TestClient with overridden dependencies.
    """
    app = borrow_modules.main.app
    get_db = borrow_modules.database.get_db
    get_current_user = borrow_modules.security.get_current_user

    def override_get_db():
        try:
            yield mock_db_session
        finally:
            pass

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()
