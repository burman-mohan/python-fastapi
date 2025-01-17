from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.models import User


def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
