from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse

from app.dependency import get_db
from app.models import File
from app.utility import retriaval, retrieval_json
from app.schemas import ChatRequest, ClientMessage, FetchJsonRequest

llm_router = APIRouter()

@llm_router.post("/stream/chat")
async def handle_chat_data_test(request: ChatRequest, protocol: str = Query('data')):
    print("request: ", request)
    print(request.messages)
    # [
    #     ClientMessage(role='user', content='What is the weather in San Francisco?', experimental_attachments=None,toolInvocations=None),
    #     ClientMessage(role='user', content='hi', experimental_attachments=None, toolInvocations=None)
    # ]

    messages = request.messages
    latest_message: ClientMessage =  messages[len(messages) - 1]
    user_query = latest_message.content
    print("User query: ", user_query)
    llm = request.llm
    collection_name = request.collection_name
    # y = ChatMessageTest(sender='AI', text='test message reply of ' + request.text)
    response = StreamingResponse(retriaval.stream_chat(user_query, collection_name, get_chat_history(messages), request.server_ip), media_type='text/event-stream')
    return response



@llm_router.post("/file/json")
async def get_file_json(request: FetchJsonRequest, protocol: str = Query('data'), db: Session = Depends(get_db)):
    file: File = db.query(File).filter(File.id == request.file_id).first()
    summary_json = retrieval_json.extract_json(file.collection_name)
    print(summary_json)
    return summary_json

def get_chat_history(messages_list: List[ClientMessage]):
    chat_history = []
    #Remove the last query which is the user question
    messages_list.pop()
    for message in messages_list:
        if message.role == "user":
            history_tuple = ("human", message.content)
            chat_history.append(history_tuple)
        else:
            history_tuple = ("ai", message.content)
            chat_history.append(history_tuple)
    return chat_history




