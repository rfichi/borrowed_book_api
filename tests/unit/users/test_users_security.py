import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import jwt
from datetime import timedelta


def test_verify_password(users_modules):
    security = users_modules.security

    password = "secret"
    hashed = security.get_password_hash(password)

    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrong", hashed) is False


def test_get_password_hash(users_modules):
    security = users_modules.security
    password = "secret"
    hashed = security.get_password_hash(password)
    assert hashed != password
    assert len(hashed) > 0


def test_create_access_token(users_modules):
    security = users_modules.security

    data = {"sub": "test@example.com"}
    token = security.create_access_token(data)

    decoded = jwt.decode(
        token, security.settings.SECRET_KEY, algorithms=[security.settings.ALGORITHM]
    )
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


def test_create_access_token_with_expires(users_modules):
    security = users_modules.security

    data = {"sub": "test@example.com"}
    expires_delta = timedelta(minutes=15)
    token = security.create_access_token(data, expires_delta=expires_delta)

    decoded = jwt.decode(
        token, security.settings.SECRET_KEY, algorithms=[security.settings.ALGORITHM]
    )
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


def test_get_current_user_success(users_modules, mock_db_session):
    security = users_modules.security
    models = users_modules.models

    # Mock jwt.decode
    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        mock_account = MagicMock(spec=models.AuthAccount)
        mock_account.user_id = 1

        mock_user = MagicMock(spec=models.User)
        mock_user.id = 1
        mock_user.email = "test@example.com"

        # Mock chaining: db.query(...).filter(...).first()
        query_mock = mock_db_session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.side_effect = [mock_account, mock_user]

        user = security.get_current_user(token="valid_token", db=mock_db_session)
        assert user == mock_user


def test_get_current_user_invalid_token(users_modules, mock_db_session):
    security = users_modules.security

    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        with pytest.raises(HTTPException) as exc:
            security.get_current_user(token="invalid_token", db=mock_db_session)
        assert exc.value.status_code == 401


def test_get_current_user_expired_token(users_modules, mock_db_session):
    security = users_modules.security

    with patch("jose.jwt.decode", side_effect=jwt.ExpiredSignatureError):
        with pytest.raises(HTTPException) as exc:
            security.get_current_user(token="expired_token", db=mock_db_session)
        assert exc.value.status_code == 401


def test_get_current_user_missing_sub(users_modules, mock_db_session):
    security = users_modules.security

    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {}  # No sub

        with pytest.raises(HTTPException) as exc:
            security.get_current_user(token="valid_token", db=mock_db_session)
        assert exc.value.status_code == 401
