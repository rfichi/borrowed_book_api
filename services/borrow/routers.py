from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import BorrowRequest, BorrowRecordOut
from service import borrow_book, return_book
from security import get_current_user

borrow_router = APIRouter(prefix="/borrow", tags=["borrow"])


@borrow_router.post("/{book_id}/borrow", response_model=BorrowRecordOut, status_code=status.HTTP_202_ACCEPTED)
def borrow_book_endpoint(book_id: int, payload: BorrowRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> BorrowRecordOut:
    record = borrow_book(db, book_id, payload.user_id)
    return record


@borrow_router.post("/{book_id}/return", response_model=BorrowRecordOut, status_code=status.HTTP_202_ACCEPTED)
def return_book_endpoint(book_id: int, payload: BorrowRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> BorrowRecordOut:
    record = return_book(db, book_id, payload.user_id)
    return record
