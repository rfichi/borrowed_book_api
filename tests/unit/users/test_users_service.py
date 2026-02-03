import pytest
from unittest.mock import patch
from fastapi import HTTPException


def test_create_user_with_password_success(users_modules, mock_db_session):
    service = users_modules.service

    name = "New User"
    email = "new@example.com"
    password = "password123"

    # Mock queries to return None (user doesn't exist)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = service.create_user_with_password(mock_db_session, name, email, password)

    assert result.name == name
    assert result.email == email

    # Verify user and account were added
    assert mock_db_session.add.call_count == 2
    assert mock_db_session.commit.call_count == 2
    assert mock_db_session.refresh.call_count == 2


def test_create_user_with_password_duplicate_email(
    users_modules, mock_db_session, mock_user
):
    service = users_modules.service

    # Mock query to return existing user
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    with pytest.raises(HTTPException) as exc:
        service.create_user_with_password(
            mock_db_session, "User", "test@example.com", "pass"
        )

    assert exc.value.status_code == 400


def test_get_user_found(users_modules, mock_db_session, mock_user):
    service = users_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    result = service.get_user(mock_db_session, 1)

    assert result == mock_user


def test_get_user_not_found(users_modules, mock_db_session):
    service = users_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = service.get_user(mock_db_session, 999)

    assert result is None


def test_list_users(users_modules, mock_db_session, mock_user):
    service = users_modules.service

    mock_db_session.query.return_value.count.return_value = 1
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [
        mock_user
    ]

    total, items = service.list_users(mock_db_session, 1, 10)

    assert total == 1
    assert len(items) == 1
    assert items[0] == mock_user


def test_get_user_borrow_history(users_modules, mock_db_session):
    service = users_modules.service
    models = users_modules.models

    mock_record = models.BorrowRecord(id=1, user_id=1, book_id=1)
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        mock_record
    ]

    history = service.get_user_borrow_history(mock_db_session, 1)

    assert len(history) == 1
    assert history[0] == mock_record


def test_authenticate_user_success(users_modules, mock_db_session):
    service = users_modules.service
    models = users_modules.models

    email = "test@example.com"
    password = "password123"
    hashed_password = "hashed_password"

    mock_account = models.AuthAccount(
        user_id=1, email=email, password_hash=hashed_password
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_account
    )

    with patch("service.verify_password", return_value=True):
        with patch("service.create_access_token", return_value="token"):
            token = service.authenticate_user(mock_db_session, email, password)
            assert token == "token"
            assert token == "token"


def test_authenticate_user_invalid(users_modules, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        users_modules.service.authenticate_user(
            mock_db_session, "test@example.com", "wrongpass"
        )

    assert exc.value.status_code == 401
