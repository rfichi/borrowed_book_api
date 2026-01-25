from sqlalchemy.orm import Session
from models import User, BorrowRecord
from schemas import UserCreate


def create_user(db: Session, data: UserCreate) -> User:
    user = User(name=data.name, email=data.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, page: int, page_size: int) -> tuple[int, list[User]]:
    q = db.query(User)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def get_user_borrow_history(db: Session, user_id: int) -> list[BorrowRecord]:
    return (
        db.query(BorrowRecord)
        .filter(BorrowRecord.user_id == user_id)
        .order_by(BorrowRecord.borrowed_at.desc())
        .all()
    )
