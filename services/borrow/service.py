"""
2026 Module responsible for defining all borrow related services
"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Book, BorrowRecord, User


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
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not book.is_available:
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
