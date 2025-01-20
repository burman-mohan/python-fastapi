from enum import Enum
from typing import List, Optional, Any

from pydantic import BaseModel


class Config:
    arbitrary_types_allowed = True

class UserBase(BaseModel):
    email: str

class UserAuth(UserBase):
    password: str

class DirectoryBase(BaseModel):
    name: str

class DirectoryCreate(DirectoryBase):
    user_email: str
    embedding_status: bool

class DirectoryId(BaseModel):
    id: int


class FileBase(BaseModel):
    name: str

class FileDelete(BaseModel):
    id: int
    directory_id: int
    file_path:str

class FileCreate(FileBase):
    doc_type: str
    file_path: str
    embedding_status: bool
    directory_id: str


class ToolInvocationState(str, Enum):
    CALL = 'call'
    PARTIAL_CALL = 'partial-call'
    RESULT = 'result'

class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str

class ToolInvocation(BaseModel):
    state: ToolInvocationState
    toolCallId: str
    toolName: str
    args: Any
    result: Any


class ClientMessage(BaseModel):
    role: str
    content: str
    experimental_attachments: Optional[List[ClientAttachment]] = None
    toolInvocations: Optional[List[ToolInvocation]] = None

class ChatRequest(BaseModel):
    messages: List[ClientMessage]
    llm: str
    collection_name: str
    server_ip: str


class FetchJsonRequest(BaseModel):
    model: str
    directory_id: str
    file_id: str




