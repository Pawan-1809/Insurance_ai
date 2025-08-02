import openai
from app.services.pinecone_client import init_pinecone
from typing import List, Dict

EMBED_MODEL = "text-embedding-ada-002"

# Get embedding for a list of texts
async def get_embeddings(texts: List[str]) -> List[List[float]]:
    response = openai.embeddings.create(
        input=texts,
        model=EMBED_MODEL
    )
    return [d.embedding for d in response.data]

# Upsert chunks to Pinecone
async def upsert_chunks_to_pinecone(chunks: List[str], doc_id: str) -> List[str]:
    index = init_pinecone()
    embeddings = await get_embeddings(chunks)
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    vectors = list(zip(ids, embeddings))
    index.upsert(vectors=vectors)
    return ids

# Query Pinecone for top_k most similar chunks
async def query_pinecone(query: str, top_k: int = 5) -> List[Dict]:
    index = init_pinecone()
    query_embedding = (await get_embeddings([query]))[0]
    res = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return res.matches
