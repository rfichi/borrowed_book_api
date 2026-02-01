from unittest.mock import patch


def test_create_book_endpoint(client, mock_book):
    payload = {"title": "Test Book", "author": "Test Author", "published_year": 2023}

    with patch(
        "services.books.routers.create_book", return_value=mock_book
    ) as mock_create:
        response = client.post("/books/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["id"] == mock_book.id

        mock_create.assert_called_once()


def test_get_book_endpoint_found(client, mock_book):
    with patch("services.books.routers.get_book", return_value=mock_book):
        response = client.get(f"/books/{mock_book.id}")

        assert response.status_code == 200
        assert response.json()["id"] == mock_book.id


def test_get_book_endpoint_not_found(client):
    with patch("services.books.routers.get_book", return_value=None):
        response = client.get("/books/999")

        assert response.status_code == 404


def test_list_books_endpoint(client, mock_book):
    with patch("services.books.routers.list_books", return_value=(1, [mock_book])):
        response = client.get("/books/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == mock_book.id


def test_delete_book_endpoint(client):
    with patch("services.books.routers.delete_book", return_value=None) as mock_delete:
        response = client.delete("/books/1")

        assert response.status_code == 204
        mock_delete.assert_called_once()


def test_update_book_availability_endpoint(client, mock_book):
    # Ensure the returned mock reflects the update
    mock_book.is_available = False
    with patch(
        "services.books.routers.update_book_availability", return_value=mock_book
    ) as mock_update:
        response = client.patch("/books/1/availability", json={"is_available": False})

        assert response.status_code == 200
        assert response.json()["is_available"] is False
        mock_update.assert_called_once()
