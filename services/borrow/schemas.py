from datetime import datetime
from pydantic import BaseModel


class BorrowRequest(BaseModel):
    user_id: int


class BorrowRecordOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrowed_at: datetime
    returned_at: datetime | None

    class Config:
        from_attributes = True
