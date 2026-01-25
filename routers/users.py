from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserOut, UserListOut, BorrowRecordOut
from services import create_user, get_user, list_users, get_user_borrow_history
from security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> UserOut:
    user = create_user(db, payload)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> UserOut:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=UserListOut)
def list_users_endpoint(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> UserListOut:
    total, items = list_users(db, page, page_size)
    return {"page": page, "page_size": page_size, "total": total, "results": items}


@router.get("/{user_id}/borrow-history", response_model=list[BorrowRecordOut])
def user_borrow_history_endpoint(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[BorrowRecordOut]:
    history = get_user_borrow_history(db, user_id)
    return history
