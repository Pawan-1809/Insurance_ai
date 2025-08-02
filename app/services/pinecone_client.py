# Pinecone vector DB client
import os
import pinecone
import os
from app.core.config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX

# TODO: Add initialization, upsert, query, and delete methods

def init_pinecone():
    api_key = (PINECONE_API_KEY or "").strip()
    env = (PINECONE_ENVIRONMENT or "").strip()
    index_name = (PINECONE_INDEX or "").strip()
    host = os.getenv("PINECONE_HOST")
    if not api_key or not env or not index_name or not host:
        raise RuntimeError("Pinecone API key, environment, index name, or host is missing or blank. Check your .env file.")
    pinecone.init(api_key=api_key, environment=env)
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=1536)
    return pinecone.Index(index_name, host=host)
