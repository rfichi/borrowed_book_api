from unittest.mock import patch, AsyncMock
import pytest


@pytest.mark.anyio
async def test_create_book_endpoint(client, mock_book):
    payload = {"title": "Test Book", "author": "Test Author", "published_year": 2023}

    with patch("routers.create_book", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_book
        response = await client.post("/books/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["id"] == mock_book.id

        mock_create.assert_called_once()


@pytest.mark.anyio
async def test_get_book_endpoint_found(client, mock_book):
    with patch("routers.get_book", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_book
        response = await client.get(f"/books/{mock_book.id}")

        assert response.status_code == 200
        assert response.json()["id"] == mock_book.id


@pytest.mark.anyio
async def test_get_book_endpoint_not_found(client):
    with patch("routers.get_book", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = await client.get("/books/999")

        assert response.status_code == 404


@pytest.mark.anyio
async def test_list_books_endpoint(client, mock_book):
    with patch("routers.list_books", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = (1, [mock_book])
        response = await client.get("/books/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == mock_book.id


@pytest.mark.anyio
async def test_delete_book_endpoint(client):
    with patch("routers.delete_book", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        response = await client.delete("/books/1")

        assert response.status_code == 204
        mock_delete.assert_called_once()


@pytest.mark.anyio
async def test_update_book_availability_endpoint(client, mock_book):
    # Ensure the returned mock reflects the update
    mock_book.is_available = False
    with patch(
        "routers.update_book_availability", new_callable=AsyncMock
    ) as mock_update:
        mock_update.return_value = mock_book
        response = await client.patch(
            "/books/1/availability", json={"is_available": False}
        )

        assert response.status_code == 200
        assert response.json()["is_available"] is False
        mock_update.assert_called_once()
