from unittest.mock import MagicMock, patch, AsyncMock
import pytest


@pytest.mark.asyncio
async def test_borrow_book_endpoint(client):
    payload = {"user_id": 1}
    book_id = 1

    # Mock the service function return value (it returns a BorrowRecord object)
    mock_record = MagicMock()
    mock_record.id = 1
    mock_record.book_id = book_id
    mock_record.user_id = 1
    mock_record.borrowed_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_record.returned_at = None

    # routers.borrow_book calls service.borrow_book which is async
    # so routers.borrow_book is async.
    # We are patching routers.borrow_book in the router module.
    # Since the endpoint awaits it, we need it to be awaitable.
    # new_callable=AsyncMock will make the mock awaitable.

    with patch("routers.borrow_book", new_callable=AsyncMock) as mock_borrow:
        mock_borrow.return_value = mock_record
        response = await client.post(f"/borrow/{book_id}/borrow", json=payload)

        assert response.status_code == 202
        mock_borrow.assert_called_once()


@pytest.mark.asyncio
async def test_return_book_endpoint(client):
    payload = {"user_id": 1}
    book_id = 1

    mock_record = MagicMock()
    mock_record.id = 1
    mock_record.book_id = book_id
    mock_record.user_id = 1
    mock_record.borrowed_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_record.returned_at.isoformat.return_value = "2024-01-02T00:00:00"

    with patch("routers.return_book", new_callable=AsyncMock) as mock_return:
        mock_return.return_value = mock_record
        response = await client.post(f"/borrow/{book_id}/return", json=payload)

        assert response.status_code == 202
        mock_return.assert_called_once()
