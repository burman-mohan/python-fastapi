from typing import List

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.utility import retriaval
from app.schemas import ChatRequest, ClientMessage

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
    response = StreamingResponse(retriaval.stream_chat(user_query, collection_name, get_chat_history(messages)), media_type='text/event-stream')
    return response

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




