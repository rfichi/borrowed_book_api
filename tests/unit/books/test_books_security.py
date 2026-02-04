import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from jose import jwt
from datetime import timedelta


def test_verify_password(books_modules):
    security = books_modules.security

    password = "secret"
    hashed = security.get_password_hash(password)

    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrong", hashed) is False


def test_get_password_hash(books_modules):
    security = books_modules.security

    password = "secret"
    hashed = security.get_password_hash(password)

    assert hashed != password
    assert security.verify_password(password, hashed) is True


def test_create_access_token(books_modules):
    security = books_modules.security
    settings = books_modules.config.get_settings()

    data = {"sub": "test@example.com"}
    token = security.create_access_token(data)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


def test_create_access_token_with_expiry(books_modules):
    security = books_modules.security
    settings = books_modules.config.get_settings()

    data = {"sub": "test@example.com"}
    expires = timedelta(minutes=10)
    token = security.create_access_token(data, expires_delta=expires)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_get_current_user_success(books_modules, mock_db_session, mock_user):
    security = books_modules.security

    # Mock jwt.decode
    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        mock_account = MagicMock()
        mock_account.user_id = 1

        # Mock query execution
        mock_account_result = MagicMock()
        mock_account_result.scalars.return_value.first.return_value = mock_account

        mock_user_result = MagicMock()
        mock_user_result.scalars.return_value.first.return_value = mock_user

        mock_db_session.execute.side_effect = [mock_account_result, mock_user_result]

        user = await security.get_current_user(token="valid_token", db=mock_db_session)
        assert user == mock_user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(books_modules, mock_db_session):
    security = books_modules.security

    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        with pytest.raises(HTTPException) as exc:
            await security.get_current_user(token="invalid_token", db=mock_db_session)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token(books_modules, mock_db_session):
    security = books_modules.security

    with patch("jose.jwt.decode", side_effect=jwt.ExpiredSignatureError):
        with pytest.raises(HTTPException) as exc:
            await security.get_current_user(token="expired_token", db=mock_db_session)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_missing_sub(books_modules, mock_db_session):
    security = books_modules.security

    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {}  # No sub

        with pytest.raises(HTTPException) as exc:
            await security.get_current_user(token="valid_token", db=mock_db_session)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_account_not_found(books_modules, mock_db_session):
    security = books_modules.security

    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc:
            await security.get_current_user(token="valid_token", db=mock_db_session)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(books_modules, mock_db_session):
    security = books_modules.security

    with patch("jose.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        mock_account = MagicMock()
        mock_account.user_id = 1

        mock_account_result = MagicMock()
        mock_account_result.scalars.return_value.first.return_value = mock_account

        mock_user_result = MagicMock()
        mock_user_result.scalars.return_value.first.return_value = None

        mock_db_session.execute.side_effect = [mock_account_result, mock_user_result]

        with pytest.raises(HTTPException) as exc:
            await security.get_current_user(token="valid_token", db=mock_db_session)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_or_internal_api_key_with_key(
    books_modules, mock_db_session
):
    security = books_modules.security
    config = books_modules.config
    settings = config.get_settings()

    # If API key matches, it returns None
    result = await security.get_current_user_or_internal_api_key(
        x_internal_api_key=settings.INTERNAL_API_KEY, token=None, db=mock_db_session
    )
    assert result is None


@pytest.mark.asyncio
async def test_get_current_user_or_internal_api_key_invalid_key(
    books_modules, mock_db_session
):
    security = books_modules.security

    # If API key is invalid, it falls through to token check which fails (None)
    with pytest.raises(HTTPException) as exc:
        await security.get_current_user_or_internal_api_key(
            x_internal_api_key="wrong_key", token=None, db=mock_db_session
        )
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_or_internal_api_key_with_token(
    books_modules, mock_db_session, mock_user
):
    security = books_modules.security

    # Mock get_current_user to avoid complexity
    with patch("security.get_current_user", new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = mock_user
        result = await security.get_current_user_or_internal_api_key(
            x_internal_api_key=None, token="valid_token", db=mock_db_session
        )
        assert result == mock_user
        mock_get_user.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_or_internal_api_key_missing_both(
    books_modules, mock_db_session
):
    security = books_modules.security

    with pytest.raises(HTTPException) as exc:
        await security.get_current_user_or_internal_api_key(
            x_internal_api_key=None, token=None, db=mock_db_session
        )
    assert exc.value.status_code == 401
