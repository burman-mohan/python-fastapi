import os

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from qdrant_client import QdrantClient, models

print("Inside db")
print(os.getenv("POSTGRES_DB_URL"))
engine = create_engine(os.getenv("POSTGRES_DB_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
with engine.begin() as conn:
    conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))


def create_tables():
    # Create tables
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#Qdrant Vector db Config
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    prefer_grpc=False,
    timeout=1000
)

def create_collection(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        timeout=100
    )
    return collection_name
