from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserOut, UserListOut, BorrowRecordOut
from service import (
    create_user, get_user, list_users, get_user_borrow_history,
    create_user_with_password, authenticate_user
)
from security import get_current_user

users_router = APIRouter(prefix="/users", tags=["users"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    user = create_user_with_password(db, name=payload.name, email=payload.email, password=payload.password)
    return user


@auth_router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = authenticate_user(db, email=form_data.username, password=form_data.password)
    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserOut)
def me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    return current_user


@users_router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@users_router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> UserOut:
    user = create_user(db, payload)
    return user


@users_router.get("/{user_id}", response_model=UserOut)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> UserOut:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@users_router.get("/", response_model=UserListOut)
@users_router.get("", response_model=UserListOut, include_in_schema=False)
def list_users_endpoint(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> UserListOut:
    total, items = list_users(db, page, page_size)
    return {"page": page, "page_size": page_size, "total": total, "results": items}


@users_router.get("/{user_id}/borrow-history", response_model=list[BorrowRecordOut])
def user_borrow_history_endpoint(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[BorrowRecordOut]:
    history = get_user_borrow_history(db, user_id)
    return history
