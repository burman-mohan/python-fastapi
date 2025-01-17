import asyncio
import os
import time
from dotenv import load_dotenv
load_dotenv()
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain.callbacks.tracers import ConsoleCallbackHandler
from app.dependency import qdrant_client
from app.utility import constants





def get_llm_model(llm_model):
    llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name=llm_model)
    return llm

def get_embedding_model_hf(model_name):
    # Load the embedding model
    model_name = model_name
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    # embeddings = HuggingFaceBgeEmbeddings(
    #     model_name=model_name,
    #     model_kwargs=model_kwargs,
    #     encode_kwargs=encode_kwargs
    # )

    hf_embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return hf_embeddings

def get_embedding_model_sentence_transformer(model_name):
    model = SentenceTransformer(
        model_name,
        trust_remote_code=True
    )
    return model

def chat_prompt_v2():
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
           which might reference context in the chat history, formulate a standalone question \
           which can be understood without the chat history. Do NOT answer the question, \
           just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    return contextualize_q_prompt


async def stream_chat(question, collection_name, chat_history):
    print("Inside stream chat")
    db = Qdrant(client=qdrant_client, embeddings=get_embedding_model_hf("sentence-transformers/all-MiniLM-L6-v2"), collection_name=collection_name)
    # condense_question_prompt, qa_prompt = prompt_templates.chat_prompt_v2()
    llm = get_llm_model(constants.LLM_LLAMA_3)
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 5, 'fetch_k': 50}
    )
    contextualize_q_prompt = chat_prompt_v2()
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt,
    )
    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\

    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    print("2")
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    print("3")

    # ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history}, config={'callbacks': [ConsoleCallbackHandler()]})
    # chat_history.extend([HumanMessage(content=question), ai_msg_1["answer"]])
    # print("4")
    # second_question = "What are the metrics in this document?"
    # ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})
    #
    # print("5")
    # print(ai_msg_2)
    # print(ai_msg_2["answer"])
    # print('*****************************************************')
    chain = rag_chain.pick("answer")
    for chunk in chain.stream({"input": question, "chat_history": chat_history}, config={'callbacks': [ConsoleCallbackHandler()]}):
        print(f"{chunk}|", end="")
        await asyncio.sleep(0.1)
        yield f"{chunk}"
    yield "\n\nsource: https://www.example.com"


async def fake_data_streamer():
    for i in range(5):
        yield f"data: This is part {i} of the response to.\n\n"
        time.sleep(1)
    yield "data: [DONE]\n\n"
    # for i in range(10):
    #     yield b'some fake data'
    #     await asyncio.sleep(0.5)


if __name__ == "__main__":
    print("Application started")
    # test("Who are the parties involved?", "jina-embedding-2", '')
    stream_chat("Who are the parties involved?", "jina-embedding-3", '')