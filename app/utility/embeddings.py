import os
import uuid
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from app.models import File, Directory
from app.dependency import qdrant_client
from qdrant_client.models import Distance, VectorParams
from app.utility import constants


def load_data_file(file_type, file_path):
    loader = None
    if file_type=='pdf':
        loader = PyPDFLoader(file_path)
    elif file_type=='docx':
        loader = Docx2txtLoader(file_path)

    return loader.load()

def split_text(loaded_document):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=500,
        chunk_overlap=50
    )
    return text_splitter.split_documents(loaded_document)

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

def create_embedding(collection_name: str, file: File):
    loaded_documents = load_data_file(file.doc_type, file.file_path)
    split_documents = split_text(loaded_documents)
    for document in split_documents:
        print("Metadata: ", document.metadata)
    texts = [doc.page_content for doc in split_documents]
    embeddings = get_embedding_model_hf("sentence-transformers/all-MiniLM-L6-v2")

    # Ensure Qdrant collection exists
    if collection_name not in qdrant_client.get_collections():
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    vectorstore = Qdrant(
        client=qdrant_client,
        collection_name=collection_name,
        embeddings=embeddings,
    )
    vectorstore.add_documents(split_documents)

    return True

