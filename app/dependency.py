from .database import SessionLocal, client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

qdrant_client = client