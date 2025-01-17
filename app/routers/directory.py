from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.models import User, Directory
from app.schemas import DirectoryCreate, UserBase
from ..services import directory

directory_router = APIRouter()

@directory_router.post("/")
def create_directory(request: DirectoryCreate, db: Session = Depends(get_db)):
    directory_create = directory.create_directory(request, db)
    return directory_create

@directory_router.post("/all")
def get_all_directories(user: UserBase, db: Session = Depends(get_db)):
    all_directory = directory.get_all_directories(user.email, db)
    if not all_directory:
        raise HTTPException(status_code=404, detail="Directory not found")
    return all_directory


@directory_router.post("/")
def create_directory(directory_create: DirectoryCreate, db: Session = Depends(get_db)):
    directory = Directory(name=directory_create.name, user_id=directory_create.user_id, embedding_status=False)
    db.add(directory)
    db.commit()
    db.refresh(directory)
    return directory