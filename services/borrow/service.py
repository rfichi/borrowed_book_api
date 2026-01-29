"""
2026 Module responsible for defining all borrow related services
"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Book, BorrowRecord, User
import httpx
import logging
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

def validate_user_via_api(user_id: int):
    """
    Validate if user exists via Users Service API.
    """
    try:
        headers = {"x-internal-api-key": settings.INTERNAL_API_KEY}
        response = httpx.get(f"{settings.USERS_SERVICE_URL}/users/{user_id}", headers=headers)
        logger.info(f"User reponse status code is {response.status_code}")
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if response.status_code != 200:
             logger.error(f"Failed to validate user {user_id}: {response.text}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"User validation failed: {response.status_code}")
    except httpx.RequestError:
        # In strict mode we might fail, for now we might fallback or fail
        # But per requirements "no book can be borrow if it does not exists" implies we must succeed in check
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Users service unavailable")

def validate_book_via_api(book_id: int):
    """
    Validate if book exists and is available via Books Service API.
    """
    try:
        headers = {"x-internal-api-key": settings.INTERNAL_API_KEY}
        response = httpx.get(f"{settings.BOOKS_SERVICE_URL}/books/{book_id}", headers=headers)
        logger.info(f"Book response status code is {response.status_code}")
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        
        if response.status_code == 200:
            book_data = response.json()
            if not book_data.get("is_available", True): # Default to true if key missing, but it should be there
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Book is already borrowed")
            return book_data
            
    except httpx.RequestError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Books service unavailable")


def get_book(db: Session, book_id: int) -> Book | None:
    """
    Retrieve a book by its ID.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book to retrieve.
    :return: The Book object if found, else None.
    """
    return db.query(Book).filter(Book.id == book_id).first()


def borrow_book(db: Session, book_id: int, user_id: int) -> BorrowRecord:
    """
    Record a user borrowing a book.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book being borrowed.
    :param user_id: ID of the user borrowing the book.
    :return: The created BorrowRecord object.
    :raises: HTTPException if book not found, user not found, or book not available.
    """
    # 1. Validate via External APIs (Sync Inter-communication)
    validate_user_via_api(user_id)
    validate_book_via_api(book_id)

    # 2. Proceed with Local Logic (Hybrid approach for POC Phase 1)
    # We still need the local objects to create the foreign key relationships 
    # and perform the atomic DB update until Pub/Sub is ready.
    book = get_book(db, book_id)
    if not book:
        # This might happen if API says yes but local DB is out of sync? 
        # For shared DB, they should match.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found locally")
    
    # We bypass local user check since we checked via API, 
    # but for FK constraint we assume user exists in shared DB.
    # If strictly decoupled, we wouldn't check User table here.
    
    if not book.is_available:
         # Double check local state for concurrency
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Book is already borrowed")

    record = BorrowRecord(user_id=user_id, book_id=book_id, borrowed_at=datetime.utcnow(), returned_at=None)
    book.is_available = False
    db.add(record)
    db.add(book)
    db.commit()
    db.refresh(record)
    return record


def return_book(db: Session, book_id: int, user_id: int) -> BorrowRecord:
    """
    Record a user returning a book.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book being returned.
    :param user_id: ID of the user returning the book.
    :return: The updated BorrowRecord object.
    :raises: HTTPException if book/user not found or no active borrow record exists.
    """
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    record = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.book_id == book_id, BorrowRecord.user_id == user_id, BorrowRecord.returned_at.is_(None))
        .order_by(BorrowRecord.borrowed_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active borrow record not found")
    record.returned_at = datetime.utcnow()
    book.is_available = True
    db.add(record)
    db.add(book)
    db.commit()
    db.refresh(record)
    return record
