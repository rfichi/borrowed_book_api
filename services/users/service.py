"""
2026 Module responsible for defining all user related services
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import User, BorrowRecord, AuthAccount
from schemas import UserCreate
from security import get_password_hash, verify_password, create_access_token


def create_user(db: Session, data: UserCreate) -> User:
    """
    Create a new user in the database.
    :param db: Database connection used to interact with database objects.
    :param data: User creation data (name, email, password).
    :return: The created User object.
    :raises: HTTPException if email is already registered.
    """
    # Use create_user_with_password to ensure auth account is created
    return create_user_with_password(db, name=data.name, email=data.email, password=data.password)


def get_user(db: Session, user_id: int) -> User | None:
    """
    Retrieve a user by their ID.
    :param db: Database connection used to interact with database objects.
    :param user_id: ID of the user to retrieve.
    :return: The User object if found, else None.
    """
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, page: int, page_size: int) -> tuple[int, list[User]]:
    """
    List users with pagination.
    :param db: Database connection used to interact with database objects.
    :param page: The page number to retrieve.
    :param page_size: The number of items per page.
    :return: A tuple containing the total count of users and the list of users for the current page.
    """
    q = db.query(User)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def get_user_borrow_history(db: Session, user_id: int) -> list[BorrowRecord]:
    """
    Retrieve the borrow history for a specific user.
    :param db: Database connection used to interact with database objects.
    :param user_id: ID of the user to retrieve history for.
    :return: A list of BorrowRecord objects for the user, ordered by borrow date descending.
    """
    return (
        db.query(BorrowRecord)
        .filter(BorrowRecord.user_id == user_id)
        .order_by(BorrowRecord.borrowed_at.desc())
        .all()
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by their email address.
    :param db: Database connection used to interact with database objects.
    :param email: The email address to search for.
    :return: The User object if found, else None.
    """
    account = db.query(AuthAccount).filter(AuthAccount.email == email).first()
    if not account:
        return None
    return db.query(User).filter(User.id == account.user_id).first()


def create_user_with_password(db: Session, name: str, email: str, password: str) -> User:
    """
    Create a new user with a password and associated auth account.
    :param db: Database connection used to interact with database objects.
    :param name: The name of the user.
    :param email: The email of the user.
    :param password: The raw password for the user.
    :return: The created User object.
    :raises: HTTPException if the email is already registered.
    """
    existing_account = db.query(AuthAccount).filter(AuthAccount.email == email).first()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_account or existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    account = AuthAccount(user_id=user.id, email=email, password_hash=get_password_hash(password))
    db.add(account)
    db.commit()
    db.refresh(account)
    return user


def authenticate_user(db: Session, email: str, password: str) -> str:
    """
    Authenticate a user and return an access token.
    :param db: Database connection used to interact with database objects.
    :param email: The email of the user attempting to login.
    :param password: The password provided by the user.
    :return: A JWT access token if authentication is successful.
    :raises: HTTPException if authentication fails.
    """
    account = db.query(AuthAccount).filter(AuthAccount.email == email).first()
    if not account or not verify_password(password, account.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token({"sub": account.email})
    return token
