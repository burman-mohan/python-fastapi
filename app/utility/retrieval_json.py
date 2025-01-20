import os
import time
from dotenv import load_dotenv
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
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



def extract_json(collection_name):
    print("collection_name: ", collection_name)
    db = Qdrant(client=qdrant_client, embeddings=get_embedding_model_hf("sentence-transformers/all-MiniLM-L6-v2"), collection_name=collection_name)
    template = """
        ### INSTRUCTION:
        The document is an Service Level Agreement.
        {context}
        Your job is to extract the detailed data from the document with source details and return them in JSON format containing the following keys: `sla name`, `parties involved`, `system concerned`, `description` and `associated metrics`.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE):

        {question}
        """
    llm = get_llm_model(constants.LLM_LLAMA_3)
    PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 5, 'fetch_k': 50}
    )
    chain_type_kwargs = {"prompt": PROMPT}
    chain = RetrievalQA.from_chain_type(llm=llm,
                                        retriever=retriever,
                                        chain_type_kwargs=chain_type_kwargs)

    results = chain({"query": ""}, return_only_outputs=True)

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(results["result"])
        print(res)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res if isinstance(res, list) else [res]



