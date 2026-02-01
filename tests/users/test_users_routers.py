from unittest.mock import MagicMock, patch


def test_signup_endpoint(client, mock_user):
    payload = {
        "name": "New User",
        "email": "new@example.com",
        "password": "password123",
    }

    with patch(
        "services.users.routers.create_user_with_password", return_value=mock_user
    ) as mock_create:
        response = client.post("/auth/signup", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == mock_user.email
        mock_create.assert_called_once()


def test_login_endpoint(client):
    with patch("services.users.routers.authenticate_user", return_value="access_token"):
        response = client.post(
            "/auth/token", data={"username": "test@example.com", "password": "password"}
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "access_token"


def test_me_endpoint(client, mock_user):
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == mock_user.email


def test_get_user_endpoint_found(client, mock_user):
    with patch("services.users.routers.get_user", return_value=mock_user):
        response = client.get(f"/users/{mock_user.id}")

        assert response.status_code == 200
        assert response.json()["id"] == mock_user.id


def test_get_user_endpoint_not_found(client):
    with patch("services.users.routers.get_user", return_value=None):
        response = client.get("/users/999")

        assert response.status_code == 404


def test_list_users_endpoint(client, mock_user):
    with patch("services.users.routers.list_users", return_value=(1, [mock_user])):
        response = client.get("/users/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["results"]) == 1


def test_user_borrow_history_endpoint(client):
    # We need to mock the object returned by service, which should match the schema
    # But service returns ORM objects. Pydantic handles conversion.
    # So we mock service returning list of objects that have these attributes

    mock_orm_record = MagicMock()
    mock_orm_record.id = 1
    mock_orm_record.book_id = 1
    mock_orm_record.user_id = 1
    mock_orm_record.borrowed_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_orm_record.returned_at = None

    with patch(
        "services.users.routers.get_user_borrow_history", return_value=[mock_orm_record]
    ):
        response = client.get("/users/1/borrow-history")

        assert response.status_code == 200
        assert len(response.json()) == 1
