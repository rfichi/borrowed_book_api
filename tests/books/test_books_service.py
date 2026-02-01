import pytest
from fastapi import HTTPException

from services.books.service import (
    create_book,
    get_book,
    list_books,
    delete_book,
    update_book_availability,
)
from services.books.schemas import BookCreate


def test_create_book(mock_db_session):
    book_data = BookCreate(title="New Book", author="New Author", published_year=2024)

    result = create_book(mock_db_session, book_data)

    assert result.title == "New Book"
    assert result.author == "New Author"
    assert result.published_year == 2024
    assert result.is_available is True

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)


def test_get_book_found(mock_db_session, mock_book):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_book
    )

    result = get_book(mock_db_session, 1)

    assert result == mock_book
    # Verify the query was constructed correctly
    # Note: testing SQLAlchemy query construction with mocks is tricky,
    # usually we just check if the result is what we expect.


def test_get_book_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = get_book(mock_db_session, 999)

    assert result is None


def test_list_books(mock_db_session, mock_book):
    mock_db_session.query.return_value.count.return_value = 1
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [
        mock_book
    ]

    total, items = list_books(mock_db_session, 1, 10)

    assert total == 1
    assert len(items) == 1
    assert items[0] == mock_book


def test_delete_book_success(mock_db_session, mock_book):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_book
    )

    delete_book(mock_db_session, 1)

    mock_db_session.delete.assert_called_once_with(mock_book)
    mock_db_session.commit.assert_called_once()


def test_delete_book_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_book(mock_db_session, 999)

    assert exc_info.value.status_code == 404
    mock_db_session.delete.assert_not_called()


def test_update_book_availability_success(mock_db_session, mock_book):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_book
    )

    result = update_book_availability(mock_db_session, 1, False)

    assert result.is_available is False
    mock_db_session.add.assert_called_with(mock_book)
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called_with(mock_book)


def test_update_book_availability_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_book_availability(mock_db_session, 999, False)

    assert exc_info.value.status_code == 404
