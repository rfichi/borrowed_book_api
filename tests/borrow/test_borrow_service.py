import pytest
from unittest.mock import patch
from fastapi import HTTPException
from services.borrow.models import BorrowRecord
from services.borrow.service import borrow_book, return_book


def test_borrow_book_success(mock_db_session):
    user_id = 1
    book_id = 1

    # Mock external API validations
    with patch("services.borrow.service.validate_user_via_api") as mock_validate_user:
        with patch(
            "services.borrow.service.validate_book_via_api"
        ) as mock_validate_book:
            with patch(
                "services.borrow.service.update_book_availability_via_api"
            ) as mock_update_book:
                result = borrow_book(mock_db_session, book_id, user_id)

                assert result.user_id == user_id
                assert result.book_id == book_id
                assert result.returned_at is None

                mock_validate_user.assert_called_once_with(user_id)
                mock_validate_book.assert_called_once_with(book_id)
                mock_update_book.assert_called_once_with(book_id, False)

                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()


def test_borrow_book_user_not_found(mock_db_session):
    with patch(
        "services.borrow.service.validate_user_via_api",
        side_effect=HTTPException(status_code=404),
    ):
        with pytest.raises(HTTPException) as exc:
            borrow_book(mock_db_session, 1, 1)
        assert exc.value.status_code == 404


def test_borrow_book_book_not_found(mock_db_session):
    with patch("services.borrow.service.validate_user_via_api"):
        with patch(
            "services.borrow.service.validate_book_via_api",
            side_effect=HTTPException(status_code=404),
        ):
            with pytest.raises(HTTPException) as exc:
                borrow_book(mock_db_session, 1, 1)
            assert exc.value.status_code == 404


def test_return_book_success(mock_db_session):
    user_id = 1
    book_id = 1

    mock_record = BorrowRecord(id=1, user_id=user_id, book_id=book_id, returned_at=None)
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
        mock_record
    )

    with patch("services.borrow.service.validate_user_via_api"):
        with patch(
            "services.borrow.service.update_book_availability_via_api"
        ) as mock_update_book:
            result = return_book(mock_db_session, book_id, user_id)

            assert result.returned_at is not None
            mock_update_book.assert_called_once_with(book_id, True)
            mock_db_session.commit.assert_called_once()


def test_return_book_no_active_record(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
        None
    )

    with patch("services.borrow.service.validate_user_via_api"):
        with pytest.raises(HTTPException) as exc:
            return_book(mock_db_session, 1, 1)
        assert exc.value.status_code == 404
