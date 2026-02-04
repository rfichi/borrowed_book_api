import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException

# Mark all tests as async
pytestmark = pytest.mark.asyncio


async def test_create_user_with_password_success(users_modules, mock_db_session):
    service = users_modules.service

    name = "New User"
    email = "new@example.com"
    password = "password123"

    # Mock execute to return empty result (no existing user)
    # The first call checks for existing account
    mock_result_account = MagicMock()
    mock_result_account.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result_account

    result = await service.create_user_with_password(
        mock_db_session, name, email, password
    )

    assert result.name == name
    assert result.email == email

    # Verify user and account were added
    assert mock_db_session.add.call_count == 2
    assert mock_db_session.commit.call_count == 2
    assert mock_db_session.refresh.call_count == 2


async def test_create_user_with_password_duplicate_email(
    users_modules, mock_db_session, mock_user
):
    service = users_modules.service

    # Mock execute to return existing user
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await service.create_user_with_password(
            mock_db_session, "User", "test@example.com", "pass"
        )

    assert exc.value.status_code == 400


async def test_get_user_found(users_modules, mock_db_session, mock_user):
    service = users_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    result = await service.get_user(mock_db_session, 1)

    assert result == mock_user


async def test_get_user_not_found(users_modules, mock_db_session):
    service = users_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await service.get_user(mock_db_session, 999)

    assert result is None


async def test_list_users(users_modules, mock_db_session, mock_user):
    service = users_modules.service

    # Mock db.scalar for count
    mock_db_session.scalar.return_value = 1

    # Mock db.execute for list
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_user]
    mock_db_session.execute.return_value = mock_result

    total, items = await service.list_users(mock_db_session, 1, 10)

    assert total == 1
    assert len(items) == 1
    assert items[0] == mock_user


async def test_get_user_borrow_history(users_modules, mock_db_session):
    service = users_modules.service
    models = users_modules.models

    mock_record = models.BorrowRecord(id=1, user_id=1, book_id=1)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_record]
    mock_db_session.execute.return_value = mock_result

    history = await service.get_user_borrow_history(mock_db_session, 1)

    assert len(history) == 1
    assert history[0] == mock_record


async def test_authenticate_user_success(users_modules, mock_db_session):
    service = users_modules.service
    models = users_modules.models

    email = "test@example.com"
    password = "password123"
    hashed_password = "hashed_password"

    mock_account = models.AuthAccount(
        user_id=1, email=email, password_hash=hashed_password
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_account
    mock_db_session.execute.return_value = mock_result

    with patch("service.verify_password", return_value=True):
        with patch("service.create_access_token", return_value="token"):
            token = await service.authenticate_user(mock_db_session, email, password)
            assert token == "token"


async def test_authenticate_user_invalid(users_modules, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await users_modules.service.authenticate_user(
            mock_db_session, "test@example.com", "wrongpass"
        )

    assert exc.value.status_code == 401


async def test_create_user_wrapper(users_modules, mock_db_session):
    service = users_modules.service
    schemas = users_modules.schemas

    user_create = schemas.UserCreate(
        name="Wrapper User", email="wrapper@example.com", password="password"
    )

    with patch(
        "service.create_user_with_password", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = "mock_user"
        result = await service.create_user(mock_db_session, user_create)

        assert result == "mock_user"
        mock_create.assert_called_once_with(
            mock_db_session,
            name=user_create.name,
            email=user_create.email,
            password=user_create.password,
        )


async def test_get_user_by_email_found(users_modules, mock_db_session, mock_user):
    service = users_modules.service
    models = users_modules.models

    email = "test@example.com"
    mock_account = models.AuthAccount(user_id=1, email=email)

    # Mock account query found
    mock_result_account = MagicMock()
    mock_result_account.scalars.return_value.first.return_value = mock_account

    mock_result_user = MagicMock()
    mock_result_user.scalars.return_value.first.return_value = mock_user

    mock_db_session.execute.side_effect = [
        mock_result_account,  # Account found
        mock_result_user,  # User found
    ]

    result = await service.get_user_by_email(mock_db_session, email)
    assert result == mock_user


async def test_get_user_by_email_not_found(users_modules, mock_db_session):
    service = users_modules.service

    # Mock account query not found
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await service.get_user_by_email(mock_db_session, "missing@example.com")
    assert result is None
