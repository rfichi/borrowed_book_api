from datetime import datetime
from typing import List
from pydantic import BaseModel, field_validator


class BookBase(BaseModel):
    title: str
    author: str
    published_year: int

    @field_validator("published_year")
    def validate_published_year(cls, v: int) -> int:
        current_year = datetime.utcnow().year
        if v > current_year:
            raise ValueError("published_year cannot be in the future")
        if v < 0:
            raise ValueError("published_year must be a positive integer")
        return v


class BookCreate(BookBase):
    pass


class AvailabilityUpdate(BaseModel):
    is_available: bool


class BookOut(BookBase):
    id: int
    is_available: bool

    class Config:
        from_attributes = True


class BookListOut(BaseModel):
    page: int
    page_size: int
    total: int
    results: List[BookOut]
