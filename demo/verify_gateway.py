import requests
import uuid
import time
import os

GATEWAY_URL = "https://borrow-gateway-bwzk395v.uc.gateway.dev"
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("Warning: API_KEY environment variable not set. Please set it before running.")
    # You might want to exit or provide a default for local testing if appropriate, 
    # but for security, it's better to fail or warn.
    # We will try to proceed but requests might fail if the gateway enforces it.

def get_headers(token=None):
    h = {"x-api-key": API_KEY}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def test_gateway():
    print(f"Testing Gateway: {GATEWAY_URL}")
    
    # 1. Signup
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "password123"
    
    print(f"1. Signup user: {email}")
    resp = requests.post(
        f"{GATEWAY_URL}/auth/signup",
        json={"name": username, "email": email, "password": password},
        headers=get_headers()
    )
    if resp.status_code == 201:
        print("   Signup SUCCESS")
        user_id = resp.json()["id"]
    elif resp.status_code == 400 and "registered" in resp.text:
         print("   User already exists (ok)")
         # Try to login to get user id is harder without a specific endpoint for "get by email", 
         # but we can list users.
         # For this script, we'll just proceed to login.
         user_id = None # Will try to fetch later
    else:
        print(f"   Signup FAILED: {resp.status_code} {resp.text}")
        return

    # 2. Login
    print("2. Login")
    resp = requests.post(
        f"{GATEWAY_URL}/auth/token",
        data={"username": email, "password": password},
        headers=get_headers()
    )
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print("   Login SUCCESS")
    else:
        print(f"   Login FAILED: {resp.status_code} {resp.text}")
        return

    # 3. List Users
    print("3. List Users")
    resp = requests.get(f"{GATEWAY_URL}/users", headers=get_headers(token))
    if resp.status_code == 200:
        users = resp.json()['results']
        print(f"   List Users SUCCESS: {len(users)} users")
        if not user_id:
             # Find our user
             for u in users:
                 if u['email'] == email:
                     user_id = u['id']
                     break
        
        # Test Get User by ID
        if user_id:
             print(f"   Testing Get User {user_id}")
             resp_u = requests.get(f"{GATEWAY_URL}/users/{user_id}", headers=get_headers(token))
             if resp_u.status_code == 200:
                 print(f"   Get User SUCCESS: {resp_u.json()['email']}")
             else:
                 print(f"   Get User FAILED: {resp_u.status_code} {resp_u.text}")
    else:
        print(f"   List Users FAILED: {resp.status_code} {resp.text}")

    if not user_id:
        print("   Could not determine user_id, aborting borrow test.")
        return

    # 4. Create Book
    print("4. Create Book")
    book_title = f"Book {uuid.uuid4().hex[:8]}"
    resp = requests.post(
        f"{GATEWAY_URL}/books",
        json={
            "title": book_title, 
            "author": "Test Author", 
            "isbn": uuid.uuid4().hex[:13],
            "published_year": 2026 # Added field
        },
        headers=get_headers(token)
    )
    if resp.status_code == 201:
        book_id = resp.json()["id"]
        print(f"   Create Book SUCCESS: ID {book_id}")
    else:
        print(f"   Create Book FAILED: {resp.status_code} {resp.text}")
        return

    # 5. List Books
    print("5. List Books")
    resp = requests.get(f"{GATEWAY_URL}/books", headers=get_headers(token))
    if resp.status_code == 200:
        print(f"   List Books SUCCESS: {len(resp.json()['results'])} books")
    else:
        print(f"   List Books FAILED: {resp.status_code} {resp.text}")

    # 5b. Get Book by ID
    print(f"5b. Get Book {book_id}")
    resp = requests.get(f"{GATEWAY_URL}/books/{book_id}", headers=get_headers(token))
    if resp.status_code == 200:
        print(f"   Get Book SUCCESS: {resp.json()['title']}")
    else:
        print(f"   Get Book FAILED: {resp.status_code} {resp.text}")

    # 6. Borrow Book
    print(f"6. Borrow Book {book_id}")
    resp = requests.post(
        f"{GATEWAY_URL}/borrow/{book_id}/borrow",
        json={"user_id": user_id},
        headers=get_headers(token)
    )
    if resp.status_code == 202:
        print("   Borrow Book SUCCESS")
    else:
        print(f"   Borrow Book FAILED: {resp.status_code} {resp.text}")

    # 7. Return Book
    print(f"7. Return Book {book_id}")
    resp = requests.post(
        f"{GATEWAY_URL}/borrow/{book_id}/return",
        json={"user_id": user_id},
        headers=get_headers(token)
    )
    if resp.status_code == 202:
        print("   Return Book SUCCESS")
    else:
        print(f"   Return Book FAILED: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_gateway()
