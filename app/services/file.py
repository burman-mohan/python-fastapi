import os
from pathlib import Path
from typing import Annotated
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import Depends, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.models import Directory, File
from app.schemas import FileDelete
from app.utility import constants
from app.utility import io_utils
from app.utility import embeddings


# def create_file(name: str, directory_id: int, db: Session = Depends(get_db)):
#
#     directory = db.query(Directory).filter(Directory.id == directory_id).first()
#     if not directory:
#         raise HTTPException(status_code=404, detail="Directory not found")
#     file = File(name=name, directory_id=directory_id)
#     db.add(file)
#     db.commit()
#     db.refresh(file)
#     return file


def create_file(files: Annotated[list[UploadFile], File()], directoryId:  Annotated[str, Form()], directoryName: Annotated[str, Form()], db: Session = Depends(get_db)):
    doc_type = ''
    for file in files:
        embedding_status = False
        print(file.content_type)
        if file.content_type == constants.DOCX_DOC_TYPE:
            doc_type = 'docx'
        elif file.content_type == constants.PDF_DOC_TYPE:
            doc_type = 'pdf'
        directory = db.query(Directory).filter(Directory.id == directoryId).first()

        path = io_utils.savefiletodisk(file, directoryId, directoryName)
        # try:
        #     embeddings.create_embedding(directory.collection_name, doc_type, path)
        #     embedding_status = True
        # except:
        #     print("Inside except")
        #     pass

        sla_file = File(doc_type=doc_type, name=file.filename, file_path=str(path),  directory_id=directoryId, embedding_status=False)
        db.add(sla_file)
        db.commit()
        db.refresh(sla_file)
        collection_name = directory.collection_name + '_' + str(sla_file.id)
        doc_embedding =  embeddings.create_embedding(collection_name, sla_file)
        embedding_status = True
        sla_file.embedding_status=True
        sla_file.collection_name = collection_name
        db.commit()
        db.refresh(sla_file)
        return sla_file

def get_all_files(directory_id, db: Session = Depends(get_db)):
    files = db.query(File).filter(File.directory_id == directory_id).all()
    return files

def delete_file(delete_file: FileDelete, db: Session = Depends(get_db)):
    io_utils.deletefile(delete_file.file_path)
    #TODO delete from qdrant collection
    result = db.query(File).filter(File.id == delete_file.id).delete()
    db.commit()
    print("result: ", result)
    return True

def get_document_stream(file_name: str, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.name == file_name).first()
    file_path = Path(file.file_path)

    if file_path.exists() and file_path.is_file():
        file_size = os.path.getsize(file_path)
        # Open the file and stream its content
        file = open(file_path, "rb")
        return StreamingResponse(file, media_type="application/octet-stream",
                                 headers={"Content-Length": str(file_size)})
    else:
        return {"error": "File not found"}
