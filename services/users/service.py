"""
2026 Module responsible for defining all user related services
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from models import User, BorrowRecord, AuthAccount
from schemas import UserCreate
from security import (
    get_password_hash,
    verify_password,
    create_access_token,
)


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """
    Create a new user in the database.
    :param db: Database connection used to interact with database objects.
    :param data: User creation data (name, email, password).
    :return: The created User object.
    :raises: HTTPException if email is already registered.
    """
    # Use create_user_with_password to ensure auth account is created
    return await create_user_with_password(
        db, name=data.name, email=data.email, password=data.password
    )


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """
    Retrieve a user by their ID.
    :param db: Database connection used to interact with database objects.
    :param user_id: ID of the user to retrieve.
    :return: The User object if found, else None.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def list_users(
    db: AsyncSession, page: int, page_size: int
) -> tuple[int, list[User]]:
    """
    List users with pagination.
    :param db: Database connection used to interact with database objects.
    :param page: The page number to retrieve.
    :param page_size: The number of items per page.
    :return: A tuple containing the total count of users and the list of users for the current page.
    """
    count_query = select(func.count()).select_from(User)
    total = await db.scalar(count_query)

    query = select(User).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return total, list(items)


async def get_user_borrow_history(db: AsyncSession, user_id: int) -> list[BorrowRecord]:
    """
    Retrieve the borrow history for a specific user.
    :param db: Database connection used to interact with database objects.
    :param user_id: ID of the user to retrieve history for.
    :return: A list of BorrowRecord objects for the user, ordered by borrow date descending.
    """
    query = (
        select(BorrowRecord)
        .where(BorrowRecord.user_id == user_id)
        .order_by(BorrowRecord.borrowed_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Retrieve a user by their email address.
    :param db: Database connection used to interact with database objects.
    :param email: The email address to search for.
    :return: The User object if found, else None.
    """
    result = await db.execute(select(AuthAccount).where(AuthAccount.email == email))
    account = result.scalars().first()
    if not account:
        return None

    result = await db.execute(select(User).where(User.id == account.user_id))
    return result.scalars().first()


async def create_user_with_password(
    db: AsyncSession, name: str, email: str, password: str
) -> User:
    """
    Create a new user with a password and associated auth account.
    :param db: Database connection used to interact with database objects.
    :param name: The name of the user.
    :param email: The email of the user.
    :param password: The raw password for the user.
    :return: The created User object.
    :raises: HTTPException if the email is already registered.
    """
    result_account = await db.execute(
        select(AuthAccount).where(AuthAccount.email == email)
    )
    existing_account = result_account.scalars().first()

    result_user = await db.execute(select(User).where(User.email == email))
    existing_user = result_user.scalars().first()

    if existing_account or existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    user = User(name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    account = AuthAccount(
        user_id=user.id, email=email, password_hash=get_password_hash(password)
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> str:
    """
    Authenticate a user and return an access token.
    :param db: Database connection used to interact with database objects.
    :param email: The email of the user attempting to login.
    :param password: The password provided by the user.
    :return: A JWT access token if authentication is successful.
    :raises: HTTPException if authentication fails.
    """
    result = await db.execute(select(AuthAccount).where(AuthAccount.email == email))
    account = result.scalars().first()

    if not account or not verify_password(password, account.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    token = create_access_token({"sub": account.email})
    return token
