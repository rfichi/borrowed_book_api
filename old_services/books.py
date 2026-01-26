from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Book, BorrowRecord, User
from schemas import BookCreate


def create_book(db: Session, data: BookCreate) -> Book:
    book = Book(title=data.title, author=data.author, published_year=data.published_year, is_available=True)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book(db: Session, book_id: int) -> Book | None:
    return db.query(Book).filter(Book.id == book_id).first()


def list_books(db: Session, page: int, page_size: int) -> tuple[int, list[Book]]:
    q = db.query(Book)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    db.delete(book)
    db.commit()


def borrow_book(db: Session, book_id: int, user_id: int) -> BorrowRecord:
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
