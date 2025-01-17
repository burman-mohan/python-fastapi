from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.models import User
from app.schemas import UserBase, UserAuth
from app.utility.app_utils import hash_password, verify_password

user_router = APIRouter()
@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserAuth, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    user = User(email=user.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@user_router.post("/login")
def login_user(users: UserAuth, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == users.email).first()
    if not user or not verify_password(users.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful"}

@user_router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user