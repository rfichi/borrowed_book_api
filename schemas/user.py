from typing import List
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserListOut(BaseModel):
    page: int
    page_size: int
    total: int
    results: List[UserOut]
