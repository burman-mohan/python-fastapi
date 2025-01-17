import shutil
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.models import Directory
from app.schemas import DirectoryId, FileDelete
from app.utility import constants
from app.services import file

file_router = APIRouter()

@file_router.post("/files")
def create_file(files: Annotated[list[UploadFile], File()], directoryId:  Annotated[str, Form()], directoryName: Annotated[str, Form()], db: Session = Depends(get_db)):
    created_file = file.create_file(files, directoryId, directoryName, db)
    return created_file

@file_router.post("/all/files")
def get_all_files(directory: DirectoryId, db: Session = Depends(get_db)):
    files = file.get_all_files(directory.id, db)
    return files

@file_router.post("/delete/file")
def delete_file(delete_file: FileDelete, db: Session = Depends(get_db)):
    status = file.delete_file(delete_file, db)
    return status