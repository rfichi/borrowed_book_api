from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add the service directory to sys.path so imports work
# Current file: tests/borrow/conftest.py
# Target: services/borrow
# sys.path.insert(0, str(Path(__file__).parents[2] / "services" / "borrow"))

# Import app and dependencies after setting up path
from services.borrow.main import app
from services.borrow.database import get_db
from services.borrow.security import get_current_user


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
def client(mock_db_session, mock_user):
    """
    Returns a TestClient with overridden dependencies.
    """

    def override_get_db():
        try:
            yield mock_db_session
        finally:
            pass

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
