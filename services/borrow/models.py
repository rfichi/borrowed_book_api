from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    published_year = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False, index=True)

    borrow_records = relationship("BorrowRecord", back_populates="book", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    borrow_records = relationship("BorrowRecord", back_populates="user", cascade="all, delete-orphan")


class AuthAccount(Base):
    __tablename__ = "auth_accounts"
    __table_args__ = (UniqueConstraint("user_id", name="uq_auth_user_id"), UniqueConstraint("email", name="uq_auth_email"))

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    user = relationship("User")


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    borrowed_at = Column(DateTime(timezone=True), nullable=False)
    returned_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")
