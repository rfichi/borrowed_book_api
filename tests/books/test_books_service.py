import pytest
from fastapi import HTTPException


def test_create_book(books_modules, mock_db_session):
    service = books_modules.service
    schemas = books_modules.schemas

    book_data = schemas.BookCreate(
        title="New Book", author="New Author", published_year=2024
    )

    result = service.create_book(mock_db_session, book_data)

    assert result.title == "New Book"
    assert result.author == "New Author"
    assert result.published_year == 2024
    assert result.is_available is True

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)


def test_get_book_found(books_modules, mock_db_session, mock_book):
    service = books_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_book
    )

    result = service.get_book(mock_db_session, 1)

    assert result == mock_book
    # Verify the query was constructed correctly
    # Note: testing SQLAlchemy query construction with mocks is tricky,
    # usually we just check if the result is what we expect.


def test_get_book_not_found(books_modules, mock_db_session):
    service = books_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = service.get_book(mock_db_session, 999)

    assert result is None


def test_list_books(books_modules, mock_db_session, mock_book):
    service = books_modules.service

    mock_db_session.query.return_value.count.return_value = 1
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [
        mock_book
    ]

    total, items = service.list_books(mock_db_session, 1, 10)

    assert total == 1
    assert len(items) == 1
    assert items[0] == mock_book


def test_delete_book_success(books_modules, mock_db_session, mock_book):
    service = books_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_book
    )

    service.delete_book(mock_db_session, 1)

    mock_db_session.delete.assert_called_once_with(mock_book)
    mock_db_session.commit.assert_called_once()


def test_delete_book_not_found(books_modules, mock_db_session):
    service = books_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.delete_book(mock_db_session, 999)

    assert exc_info.value.status_code == 404
    mock_db_session.delete.assert_not_called()


def test_update_book_availability_success(books_modules, mock_db_session, mock_book):
    service = books_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_book
    )

    result = service.update_book_availability(mock_db_session, 1, False)

    assert result.is_available is False
    mock_db_session.add.assert_called_with(mock_book)
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called_with(mock_book)


def test_update_book_availability_not_found(books_modules, mock_db_session):
    service = books_modules.service

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.update_book_availability(mock_db_session, 1, False)

    assert exc_info.value.status_code == 404
