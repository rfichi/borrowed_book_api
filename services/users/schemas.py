from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class BorrowRecordOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrowed_at: datetime
    returned_at: datetime | None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserListOut(BaseModel):
    page: int
    page_size: int
    total: int
    results: List[UserOut]
