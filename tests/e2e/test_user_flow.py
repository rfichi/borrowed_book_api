import uuid
import pytest


@pytest.mark.e2e
def test_full_user_journey(client):
    # 1. Signup
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "password123"

    print(f"1. Signup user: {email}")
    resp = client.post(
        "/auth/signup",
        json={"name": username, "email": email, "password": password},
    )

    user_id = None
    if resp.status_code == 400 and "registered" in resp.text:
        # If user exists, we continue (though with random uuid this shouldn't happen often)
        pass
    else:
        assert resp.status_code == 201, f"Signup failed: {resp.text}"
        user_id = resp.json()["id"]

    # 2. Login
    print("2. Login")
    resp = client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]

    # Update headers with token
    # Client has base headers, we need to update them for subsequent requests?
    # Or just pass headers to subsequent requests.
    # httpx.Client headers are merged.
    client.headers.update({"Authorization": f"Bearer {token}"})

    # 3. List Users & Get User ID (if needed)
    print("3. List Users")
    resp = client.get("/users")
    assert resp.status_code == 200, f"List users failed: {resp.text}"
    users = resp.json()["results"]

    # Find our user if we didn't get ID from signup (e.g. if we handled existing user)
    if not user_id:
        found_user = next((u for u in users if u["email"] == email), None)
        assert (
            found_user is not None
        ), "Created user not found in users list (and signup returned existing)"
        user_id = found_user["id"]
    else:
        # We have the ID, just optionally check if it's in the list (but don't fail if pagination hides it)
        found_user = next((u for u in users if u["email"] == email), None)
        if found_user:
            print(f"   User found in first page of users list: {found_user['id']}")
        else:
            print(
                "   User NOT found in first page of users list (likely due to pagination)"
            )

    # Test Get User by ID
    print(f"   Testing Get User {user_id}")
    resp_u = client.get(f"/users/{user_id}")
    assert resp_u.status_code == 200, f"Get user failed: {resp_u.text}"
    assert resp_u.json()["email"] == email

    # 4. Create Book
    print("4. Create Book")
    book_title = f"Book {uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/books",
        json={
            "title": book_title,
            "author": "Test Author",
            "isbn": uuid.uuid4().hex[:13],
            "published_year": 2026,
        },
    )
    assert resp.status_code == 201, f"Create book failed: {resp.text}"
    book_id = resp.json()["id"]

    # 5. List Books
    print("5. List Books")
    resp = client.get("/books")
    assert resp.status_code == 200, f"List books failed: {resp.text}"

    # 5b. Get Book by ID
    print(f"5b. Get Book {book_id}")
    resp = client.get(f"/books/{book_id}")
    assert resp.status_code == 200, f"Get book failed: {resp.text}"
    assert resp.json()["title"] == book_title

    # 6. Borrow Book
    print(f"6. Borrow Book {book_id}")
    resp = client.post(
        f"/borrow/{book_id}/borrow",
        json={"user_id": user_id},
    )
    assert resp.status_code == 202, f"Borrow book failed: {resp.text}"

    # 7. Return Book
    print(f"7. Return Book {book_id}")
    resp = client.post(
        f"/borrow/{book_id}/return",
        json={"user_id": user_id},
    )
    assert resp.status_code == 202, f"Return book failed: {resp.text}"

    # 8. Borrow History
    print(f"8. Borrow History for user {user_id}")
    resp = client.get(f"/users/{user_id}/borrow-history")
    assert resp.status_code == 200, f"Borrow history failed: {resp.text}"
    history = resp.json()
    # We expect at least 1 record (the one we just did)
    assert len(history) >= 1

    # 9. Edge Cases: Non-existent User/Book
    print("9. Testing Edge Cases")

    # 9.1 Borrow with Non-existent User
    non_existent_user_id = 999999
    resp = client.post(
        f"/borrow/{book_id}/borrow",
        json={"user_id": non_existent_user_id},
    )
    assert resp.status_code == 404, "Borrow with non-existent user should fail with 404"

    # 9.2 Borrow Non-existent Book
    non_existent_book_id = 999999
    resp = client.post(
        f"/borrow/{non_existent_book_id}/borrow",
        json={"user_id": user_id},
    )
    # Note: If the book service checks existence, it returns 404.
    # The current logic in verify_gateway.py expects 404 or 400 depending on implementation.
    # We'll assert 404 based on verify_gateway.py logic (it doesn't explicit check 404 there but logs it).
    # Let's assume 404.
    assert resp.status_code == 404, "Borrow non-existent book should fail with 404"
