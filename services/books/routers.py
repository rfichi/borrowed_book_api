from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import BookCreate, BookOut, BookListOut
from service import create_book, get_book, list_books, delete_book
from security import get_current_user, get_current_user_or_internal_api_key

books_router = APIRouter(prefix="/books", tags=["books"])


@books_router.post("/", response_model=BookOut, status_code=status.HTTP_201_CREATED)
@books_router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_book_endpoint(payload: BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> BookOut:
    book = create_book(db, payload)
    return book


@books_router.get("/{book_id}", response_model=BookOut)
def get_book_endpoint(book_id: int, db: Session = Depends(get_db), auth=Depends(get_current_user_or_internal_api_key)) -> BookOut:
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@books_router.get("/", response_model=BookListOut)
@books_router.get("", response_model=BookListOut, include_in_schema=False)
def list_books_endpoint(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> BookListOut:
    total, items = list_books(db, page, page_size)
    return {"page": page, "page_size": page_size, "total": total, "results": items}


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_endpoint(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> None:
    delete_book(db, book_id)
    return None
