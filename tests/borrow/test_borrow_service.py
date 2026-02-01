import pytest
from unittest.mock import patch
from fastapi import HTTPException


def test_borrow_book_success(borrow_modules, mock_db_session):
    service = borrow_modules.service

    user_id = 1
    book_id = 1

    # Mock external API validations
    with patch("service.validate_user_via_api") as mock_validate_user:
        with patch("service.validate_book_via_api") as mock_validate_book:
            with patch("service.update_book_availability_via_api") as mock_update_book:
                result = service.borrow_book(mock_db_session, book_id, user_id)

                assert result.user_id == user_id
                assert result.book_id == book_id
                assert result.returned_at is None

                mock_validate_user.assert_called_once_with(user_id)
                mock_validate_book.assert_called_once_with(book_id)
                mock_update_book.assert_called_once_with(book_id, False)

                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()


def test_borrow_book_user_not_found(borrow_modules, mock_db_session):
    service = borrow_modules.service

    with patch(
        "service.validate_user_via_api",
        side_effect=HTTPException(status_code=404),
    ):
        with pytest.raises(HTTPException) as exc:
            service.borrow_book(mock_db_session, 1, 1)
        assert exc.value.status_code == 404


def test_borrow_book_book_not_found(borrow_modules, mock_db_session):
    service = borrow_modules.service

    with patch("service.validate_user_via_api"):
        with patch(
            "service.validate_book_via_api",
            side_effect=HTTPException(status_code=404),
        ):
            with pytest.raises(HTTPException) as exc:
                service.borrow_book(mock_db_session, 1, 1)
            assert exc.value.status_code == 404


def test_return_book_success(borrow_modules, mock_db_session):
    service = borrow_modules.service
    models = borrow_modules.models

    user_id = 1
    book_id = 1

    mock_record = models.BorrowRecord(
        id=1, user_id=user_id, book_id=book_id, returned_at=None
    )
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
        mock_record
    )

    with patch("service.validate_user_via_api"):
        with patch("service.update_book_availability_via_api") as mock_update_book:
            result = service.return_book(mock_db_session, book_id, user_id)

            assert result.returned_at is not None
            mock_update_book.assert_called_once_with(book_id, True)
            mock_db_session.commit.assert_called_once()


def test_return_book_no_active_record(borrow_modules, mock_db_session):
    service = borrow_modules.service

    mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
        None
    )

    with patch("service.validate_user_via_api"):
        with pytest.raises(HTTPException) as exc:
            service.return_book(mock_db_session, 1, 1)
        assert exc.value.status_code == 404
