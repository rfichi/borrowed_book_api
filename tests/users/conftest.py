from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add the service directory to sys.path so imports work
# Current file: tests/users/conftest.py
# Target: services/users
# We need to make sure we're not accidentally importing from books or other services
# sys.path.insert(0, str(Path(__file__).parents[2] / "services" / "users"))

# Import app and dependencies after setting up path
from services.users.main import app
from services.users.database import get_db
from services.users.security import (
    get_current_user,
    get_current_user_or_internal_api_key,
)
from services.users.models import User


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_user():
    """Returns a mock user."""
    return User(id=1, name="Test User", email="test@example.com")


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

    def override_get_current_user_or_api_key():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[
        get_current_user_or_internal_api_key
    ] = override_get_current_user_or_api_key

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
