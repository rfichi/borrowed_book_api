from unittest.mock import MagicMock, patch


def test_borrow_book_endpoint(client):
    payload = {"user_id": 1}
    book_id = 1

    # Mock the service function return value (it returns a BorrowRecord object)
    mock_record = MagicMock()
    mock_record.id = 1
    mock_record.book_id = book_id
    mock_record.user_id = 1
    mock_record.borrowed_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_record.returned_at = None

    with patch(
        "services.borrow.routers.borrow_book", return_value=mock_record
    ) as mock_borrow:
        response = client.post(f"/borrow/{book_id}/borrow", json=payload)

        assert response.status_code == 202
        mock_borrow.assert_called_once()


def test_return_book_endpoint(client):
    payload = {"user_id": 1}
    book_id = 1

    mock_record = MagicMock()
    mock_record.id = 1
    mock_record.book_id = book_id
    mock_record.user_id = 1
    mock_record.borrowed_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_record.returned_at.isoformat.return_value = "2024-01-02T00:00:00"

    with patch(
        "services.borrow.routers.return_book", return_value=mock_record
    ) as mock_return:
        response = client.post(f"/borrow/{book_id}/return", json=payload)

        assert response.status_code == 202
        mock_return.assert_called_once()
