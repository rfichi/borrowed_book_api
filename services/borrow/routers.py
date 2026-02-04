import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import BorrowRequest, BorrowRecordOut
from service import borrow_book, return_book
from security import get_current_user

_logger = logging.getLogger(__name__)
borrow_router = APIRouter(prefix="/borrow", tags=["borrow"])


@borrow_router.post(
    "/{book_id}/borrow",
    response_model=BorrowRecordOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def borrow_book_endpoint(
    book_id: int,
    payload: BorrowRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> BorrowRecordOut:
    record = await borrow_book(db, book_id, payload.user_id)
    _logger.info(f"Borrowed book {book_id} for user {payload.user_id}")
    return record


@borrow_router.post(
    "/{book_id}/return",
    response_model=BorrowRecordOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def return_book_endpoint(
    book_id: int,
    payload: BorrowRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> BorrowRecordOut:
    record = await return_book(db, book_id, payload.user_id)
    return record
