from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv()
import os
from app.database import create_tables
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from app.routers.directory import directory_router
from app.routers.file import file_router
from app.routers.user import user_router
from app.routers.llm import llm_router


# Startup event
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application started..")
    create_tables()
    yield
    # Clean up the ML models and release the resources
    print("..Application ended")



app = FastAPI(lifespan=lifespan)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(directory_router, prefix="/api/directories", tags=["Directories"])
app.include_router(file_router, prefix="/api/file", tags=["Files"])
app.include_router(llm_router, prefix="/api/llm", tags=["Llm"])




