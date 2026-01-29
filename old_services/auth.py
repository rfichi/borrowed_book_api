from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import User, AuthAccount
from security import get_password_hash, verify_password, create_access_token


def get_user_by_email(db: Session, email: str) -> User | None:
    account = db.query(AuthAccount).filter(AuthAccount.email == email).first()
    if not account:
        return None
    return db.query(User).filter(User.id == account.user_id).first()


def create_user_with_password(db: Session, name: str, email: str, password: str) -> User:
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
    account = db.query(AuthAccount).filter(AuthAccount.email == email).first()
    if not account or not verify_password(password, account.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token({"sub": account.email})
    return token
