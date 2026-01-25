from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import BookCreate, BookOut, BookListOut, BorrowRequest, BorrowRecordOut
from services import create_book, get_book, list_books, delete_book, borrow_book, return_book
from security import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book_endpoint(payload: BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> BookOut:
    book = create_book(db, payload)
    return book


@router.get("/{book_id}", response_model=BookOut)
def get_book_endpoint(book_id: int, db: Session = Depends(get_db)) -> BookOut:
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.get("/", response_model=BookListOut)
def list_books_endpoint(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)) -> BookListOut:
    total, items = list_books(db, page, page_size)
    return {"page": page, "page_size": page_size, "total": total, "results": items}


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_endpoint(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> None:
    delete_book(db, book_id)
    return None


@router.post("/{book_id}/borrow", response_model=BorrowRecordOut, status_code=status.HTTP_202_ACCEPTED)
def borrow_book_endpoint(book_id: int, payload: BorrowRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> BorrowRecordOut:
    record = borrow_book(db, book_id, payload.user_id)
    return record


@router.post("/{book_id}/return", response_model=BorrowRecordOut, status_code=status.HTTP_202_ACCEPTED)
def return_book_endpoint(book_id: int, payload: BorrowRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> BorrowRecordOut:
    record = return_book(db, book_id, payload.user_id)
    return record
