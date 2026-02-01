import pytest
from unittest.mock import patch
from fastapi import HTTPException
from services.users.service import (
    get_user,
    list_users,
    get_user_borrow_history,
    create_user_with_password,
    authenticate_user,
)
from services.users.models import BorrowRecord, AuthAccount


def test_create_user_with_password_success(mock_db_session):
    name = "New User"
    email = "new@example.com"
    password = "password123"

    # Mock queries to return None (user doesn't exist)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = create_user_with_password(mock_db_session, name, email, password)

    assert result.name == name
    assert result.email == email

    # Verify user and account were added
    assert mock_db_session.add.call_count == 2
    assert mock_db_session.commit.call_count == 2
    assert mock_db_session.refresh.call_count == 2


def test_create_user_with_password_duplicate_email(mock_db_session, mock_user):
    # Mock query to return existing user
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    with pytest.raises(HTTPException) as exc:
        create_user_with_password(mock_db_session, "User", "test@example.com", "pass")

    assert exc.value.status_code == 400


def test_get_user_found(mock_db_session, mock_user):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    result = get_user(mock_db_session, 1)

    assert result == mock_user


def test_get_user_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = get_user(mock_db_session, 999)

    assert result is None


def test_list_users(mock_db_session, mock_user):
    mock_db_session.query.return_value.count.return_value = 1
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [
        mock_user
    ]

    total, items = list_users(mock_db_session, 1, 10)

    assert total == 1
    assert len(items) == 1
    assert items[0] == mock_user


def test_get_user_borrow_history(mock_db_session):
    mock_record = BorrowRecord(id=1, user_id=1, book_id=1)
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        mock_record
    ]

    history = get_user_borrow_history(mock_db_session, 1)

    assert len(history) == 1
    assert history[0] == mock_record


def test_authenticate_user_success(mock_db_session):
    email = "test@example.com"
    password = "password123"
    hashed_password = "hashed_password"

    mock_account = AuthAccount(user_id=1, email=email, password_hash=hashed_password)
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_account
    )

    with patch("services.users.service.verify_password", return_value=True):
        with patch("services.users.service.create_access_token", return_value="token"):
            token = authenticate_user(mock_db_session, email, password)
            assert token == "token"


def test_authenticate_user_invalid(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        authenticate_user(mock_db_session, "test@example.com", "wrongpass")

    assert exc.value.status_code == 401
