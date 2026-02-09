"""
2026 Module responsible for defining all borrow related services
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from models import BorrowRecord
import httpx
import logging
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


async def validate_user_via_api(user_id: int):
    """
    Validate if user exists via Users Service API.
    """
    try:
        headers = {"x-internal-api-key": settings.INTERNAL_API_KEY}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.USERS_SERVICE_URL}/users/{user_id}", headers=headers
            )
        logger.info(f"User reponse status code is {response.status_code}")
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if response.status_code != 200:
            logger.error(f"Failed to validate user {user_id}: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User validation failed: {response.status_code}",
            )
    except httpx.RequestError:
        # In strict mode we might fail, for now we might fallback or fail
        # But per requirements "no book can be borrow if it does not exists" implies we must succeed in check
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Users service unavailable",
        )


async def validate_book_via_api(book_id: int):
    """
    Validate if book exists and is available via Books Service API.
    """
    try:
        headers = {"x-internal-api-key": settings.INTERNAL_API_KEY}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.BOOKS_SERVICE_URL}/books/{book_id}", headers=headers
            )
        logger.info(f"Book response status code is {response.status_code}")
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        if response.status_code == 200:
            book_data = response.json()
            if not book_data.get(
                "is_available", True
            ):  # Default to true if key missing, but it should be there
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Book is already borrowed",
                )
            return book_data

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Books service unavailable",
        )


async def update_book_availability_via_api(book_id: int, is_available: bool):
    """
    Update the availability status of a book via the Books Service API.
    """
    try:
        headers = {"x-internal-api-key": settings.INTERNAL_API_KEY}
        payload = {"is_available": is_available}
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{settings.BOOKS_SERVICE_URL}/books/{book_id}/availability",
                headers=headers,
                json=payload,
            )
        logger.info(
            f"Update book availability response status code: {response.status_code}"
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )
        if response.status_code != 200:
            logger.error(
                f"Failed to update book {book_id} availability: {response.text}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Book update failed: {response.status_code}",
            )
        return response.json()
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Books service unavailable",
        )


async def borrow_book(db: AsyncSession, book_id: int, user_id: int) -> BorrowRecord:
    """
    Record a user borrowing a book.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book being borrowed.
    :param user_id: ID of the user borrowing the book.
    :return: The created BorrowRecord object.
    :raises: HTTPException if book not found, user not found, or book not available.
    """
    # 1. Validate via External APIs (Sync Inter-communication)
    await validate_user_via_api(user_id)
    await validate_book_via_api(book_id)

    # 2. Update Book Availability via API
    await update_book_availability_via_api(book_id, False)

    # 3. Create Borrow Record locally
    record = BorrowRecord(
        user_id=user_id,
        book_id=book_id,
        borrowed_at=datetime.utcnow(),
        returned_at=None,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def return_book(db: AsyncSession, book_id: int, user_id: int) -> BorrowRecord:
    """
    Record a user returning a book.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book being returned.
    :param user_id: ID of the user returning the book.
    :return: The updated BorrowRecord object.
    :raises: HTTPException if book/user not found or no active borrow record exists.
    """
    # 1. Validate via External APIs
    await validate_user_via_api(user_id)
    # We don't necessarily need to validate book existence if we are returning it,
    # but we should check if an active record exists.

    # 2. Find Active Borrow Record
    result = await db.execute(
        select(BorrowRecord)
        .filter(
            BorrowRecord.book_id == book_id,
            BorrowRecord.user_id == user_id,
            BorrowRecord.returned_at.is_(None),
        )
        .order_by(BorrowRecord.borrowed_at.desc())
    )
    record = result.scalars().first()

    if not record:
        # Check for inconsistency: Book is marked borrowed in Books Service, but no record here.
        # This can happen if the borrow process failed mid-way or data was manually altered.
        try:
            # Check if book is available. If it raises 403, it means it IS borrowed.
            await validate_book_via_api(book_id)

            # If we get here, the book is AVAILABLE.
            # So it is not borrowed, and thus cannot be returned.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active borrow record not found",
            )
        except HTTPException as e:
            if e.status_code == status.HTTP_403_FORBIDDEN:
                # Book IS borrowed. We assume it corresponds to this user to allow recovery.
                logger.warning(
                    f"Inconsistency detected: Book {book_id} is borrowed but no record found for user {user_id}. "
                    "Creating recovery record and proceeding with return."
                )
                record = BorrowRecord(
                    user_id=user_id,
                    book_id=book_id,
                    borrowed_at=datetime.utcnow(),
                    returned_at=None,
                )
                db.add(record)
                # Proceed to return flow
            else:
                # Other errors (e.g. 404 Not Found, 503 Service Unavailable) should propagate
                raise e

    # 3. Update Book Availability via API
    await update_book_availability_via_api(book_id, True)

    # 4. Update local Borrow Record
    record.returned_at = datetime.utcnow()
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
