import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from services.books.security import (
    get_current_user,
    get_current_user_or_internal_api_key,
)
from services.books.config import get_settings

settings = get_settings()


def test_get_current_user_success(mock_db_session, mock_user):
    # Mock jwt.decode
    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        mock_account = MagicMock()
        mock_account.user_id = 1

        # Mock chaining: db.query(...).filter(...).first()
        # We need first() to return account then user

        # Create a mock for the query result
        query_mock = mock_db_session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.side_effect = [mock_account, mock_user]

        user = get_current_user(token="valid_token", db=mock_db_session)
        assert user == mock_user


def test_get_current_user_invalid_token(mock_db_session):
    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        with pytest.raises(HTTPException) as exc:
            get_current_user(token="invalid_token", db=mock_db_session)
        assert exc.value.status_code == 401


def test_get_current_user_account_not_found(mock_db_session):
    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            get_current_user(token="valid_token", db=mock_db_session)
        assert exc.value.status_code == 401


def test_get_current_user_or_internal_api_key_with_key(mock_db_session):
    # If API key matches, it returns None
    result = get_current_user_or_internal_api_key(
        x_internal_api_key=settings.INTERNAL_API_KEY, token=None, db=mock_db_session
    )
    assert result is None


def test_get_current_user_or_internal_api_key_with_token(mock_db_session, mock_user):
    # Mock get_current_user to avoid complexity
    with patch(
        "services.books.security.get_current_user", return_value=mock_user
    ) as mock_get_user:
        result = get_current_user_or_internal_api_key(
            x_internal_api_key=None, token="valid_token", db=mock_db_session
        )
        assert result == mock_user
        mock_get_user.assert_called_once()


def test_get_current_user_or_internal_api_key_missing_both(mock_db_session):
    with pytest.raises(HTTPException) as exc:
        get_current_user_or_internal_api_key(
            x_internal_api_key=None, token=None, db=mock_db_session
        )
    assert exc.value.status_code == 401
