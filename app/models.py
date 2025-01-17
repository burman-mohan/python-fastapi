import time
from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Directory(Base):
    __tablename__ = "directories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    path = Column(String, nullable=True)
    collection_name= Column(String, nullable=True)
    json_insight = Column(String, nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    embedding_status = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="directories")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    collection_name = Column(String, nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    embedding_status = Column(Boolean, nullable=False)
    directory_id = Column(Integer, ForeignKey("directories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    directory = relationship("Directory", back_populates="files")


User.directories = relationship("Directory", back_populates="user", cascade="all, delete")
Directory.files = relationship("File", back_populates="directory", cascade="all, delete")