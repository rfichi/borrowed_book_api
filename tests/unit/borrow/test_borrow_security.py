from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from jose import jwt
from datetime import timedelta


def test_verify_password(borrow_modules):
    security = borrow_modules.security

    # These are wrappers around passlib, but we can test they work
    password = "secret"
    hashed = security.get_password_hash(password)

    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrong", hashed) is False


def test_get_password_hash(borrow_modules):
    security = borrow_modules.security

    password = "secret"
    hashed = security.get_password_hash(password)

    assert hashed != password
    assert security.verify_password(password, hashed) is True


def test_create_access_token(borrow_modules):
    security = borrow_modules.security
    settings = borrow_modules.config.get_settings()

    data = {"sub": "test@example.com"}
    token = security.create_access_token(data)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


def test_create_access_token_with_expiry(borrow_modules):
    security = borrow_modules.security
    settings = borrow_modules.config.get_settings()

    data = {"sub": "test@example.com"}
    expires = timedelta(minutes=10)
    token = security.create_access_token(data, expires_delta=expires)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


def test_get_current_user_success(borrow_modules, mock_db_session, mock_user):
    security = borrow_modules.security
    models = borrow_modules.models

    # Mock jwt.decode
    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        mock_account = MagicMock(spec=models.AuthAccount)
        mock_account.user_id = 1

        # Mock chaining: db.query(...).filter(...).first()
        query_mock = mock_db_session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.side_effect = [mock_account, mock_user]

        user = security.get_current_user(token="valid_token", db=mock_db_session)
        assert user == mock_user


def test_get_current_user_invalid_token(borrow_modules, mock_db_session):
    security = borrow_modules.security

    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        with pytest.raises(HTTPException) as exc:
            security.get_current_user(token="invalid_token", db=mock_db_session)
        assert exc.value.status_code == 401


def test_get_current_user_expired_token(borrow_modules, mock_db_session):
    security = borrow_modules.security

    with patch("jose.jwt.decode", side_effect=jwt.ExpiredSignatureError):
        with pytest.raises(HTTPException) as exc:
            security.get_current_user(token="expired_token", db=mock_db_session)
        assert exc.value.status_code == 401


def test_get_current_user_missing_sub(borrow_modules, mock_db_session):
    security = borrow_modules.security

    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {}  # No sub

        with pytest.raises(HTTPException) as exc:
            security.get_current_user(token="valid_token", db=mock_db_session)
        assert exc.value.status_code == 401
