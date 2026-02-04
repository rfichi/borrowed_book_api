import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

pytestmark = pytest.mark.asyncio


async def test_create_book(books_modules, mock_db_session):
    service = books_modules.service
    schemas = books_modules.schemas

    book_data = schemas.BookCreate(
        title="New Book", author="New Author", published_year=2024
    )

    result = await service.create_book(mock_db_session, book_data)

    assert result.title == "New Book"
    assert result.author == "New Author"
    assert result.published_year == 2024
    assert result.is_available is True

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)


async def test_get_book_found(books_modules, mock_db_session, mock_book):
    service = books_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_book
    mock_db_session.execute.return_value = mock_result

    result = await service.get_book(mock_db_session, 1)

    assert result == mock_book


async def test_get_book_not_found(books_modules, mock_db_session):
    service = books_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await service.get_book(mock_db_session, 999)

    assert result is None


async def test_list_books(books_modules, mock_db_session, mock_book):
    service = books_modules.service

    # First call is for count, second for items
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 1

    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = [mock_book]

    mock_db_session.execute.side_effect = [mock_count_result, mock_items_result]

    total, items = await service.list_books(mock_db_session, 1, 10)

    assert total == 1
    assert len(items) == 1
    assert items[0] == mock_book


async def test_delete_book_success(books_modules, mock_db_session, mock_book):
    service = books_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_book
    mock_db_session.execute.return_value = mock_result

    await service.delete_book(mock_db_session, 1)

    mock_db_session.delete.assert_called_once_with(mock_book)
    mock_db_session.commit.assert_called_once()


async def test_delete_book_not_found(books_modules, mock_db_session):
    service = books_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_book(mock_db_session, 999)

    assert exc_info.value.status_code == 404
    mock_db_session.delete.assert_not_called()


async def test_update_book_availability_success(
    books_modules, mock_db_session, mock_book
):
    service = books_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_book
    mock_db_session.execute.return_value = mock_result

    result = await service.update_book_availability(mock_db_session, 1, False)

    assert result.is_available is False
    mock_db_session.add.assert_called_with(mock_book)
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called_with(mock_book)


async def test_update_book_availability_not_found(books_modules, mock_db_session):
    service = books_modules.service

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await service.update_book_availability(mock_db_session, 1, False)

    assert exc_info.value.status_code == 404
