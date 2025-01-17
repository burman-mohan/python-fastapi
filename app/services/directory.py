from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from .user import get_user_by_email
from ..utility.io_utils import create_directory_in_disk
from app.dependency import get_db
from app.models import Directory, User
from app.schemas import DirectoryCreate
from ..database import create_collection
from langchain_community.vectorstores.falkordb_vector import generate_random_string


def create_directory(directory_create: DirectoryCreate, db: Session = Depends(get_db)):
    user: User = get_user_by_email(directory_create.user_email, db)
    directory = Directory(name=directory_create.name, user_id=user.id, embedding_status=False)
    db.add(directory)
    db.commit()
    db.refresh(directory)
    directory_path = create_directory_in_disk(directory.name, directory.id)
    collection_name = create_collection(generate_random_string(20))
    directory = update_directory(directory.id, directory_path, collection_name, db)
    return directory

def get_all_directories(user_email: str, db: Session = Depends(get_db)):
    user: User = get_user_by_email(user_email, db)
    directory = db.query(Directory).filter(Directory.user_id == user.id).all()
    if not directory:
        raise HTTPException(status_code=404, detail="Directory not found")
    return directory

#Update collection name and directory path
def update_directory(id:int, directory_path:str, collection_name: str, db: Session = Depends(get_db)):
    directory = db.query(Directory).filter(Directory.id == id).first()
    if not directory:
        raise HTTPException(status_code=404, detail="Directory not found")
    directory.collection_name  = collection_name
    directory.path= directory_path
    db.commit()
    return directory

