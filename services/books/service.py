"""
2026 Module responsible for defining all book related services
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from models import Book
from schemas import BookCreate


async def create_book(db: AsyncSession, data: BookCreate) -> Book:
    """
    Create a new book in the database.
    :param db: Database connection used to interact with database objects.
    :param data: Book creation data (title, author, published_year).
    :return: The created Book object.
    """
    book = Book(
        title=data.title,
        author=data.author,
        published_year=data.published_year,
        is_available=True,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def get_book(db: AsyncSession, book_id: int) -> Book | None:
    """
    Retrieve a book by its ID.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book to retrieve.
    :return: The Book object if found, else None.
    """
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalars().first()


async def list_books(
    db: AsyncSession, page: int, page_size: int
) -> tuple[int, list[Book]]:
    """
    List books with pagination.
    :param db: Database connection used to interact with database objects.
    :param page: The page number to retrieve.
    :param page_size: The number of items per page.
    :return: A tuple containing the total count of books and the list of books for the current page.
    """
    count_query = select(func.count()).select_from(Book)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = select(Book).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return total, items


async def delete_book(db: AsyncSession, book_id: int) -> None:
    """
    Delete a book from the database.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book to delete.
    :return: None
    :raises: HTTPException if the book is not found.
    """
    book = await get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    await db.delete(book)
    await db.commit()


async def update_book_availability(
    db: AsyncSession, book_id: int, is_available: bool
) -> Book:
    """
    Update the availability status of a book.
    :param db: Database connection used to interact with database objects.
    :param book_id: ID of the book to update.
    :param is_available: The new availability status.
    :return: The updated Book object.
    :raises: HTTPException if the book is not found.
    """
    book = await get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    book.is_available = is_available
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book
