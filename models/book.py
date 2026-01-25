from sqlalchemy import Column, Integer, String, Boolean
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
