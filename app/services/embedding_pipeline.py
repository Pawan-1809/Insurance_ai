
import openai
import requests
from app.services.faiss_client import faiss_index
from typing import List, Dict
import logging
from app.core.config import EMBEDDING_MODEL, OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Get embedding for a list of texts
async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings for a list of texts using OpenAI's embedding model."""
    try:
        # Try OpenAI client first
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.embeddings.create(
                input=texts,
                model=EMBEDDING_MODEL
            )
            return [d.embedding for d in response.data]
            
        except Exception as client_error:
            logger.warning(f"OpenAI client failed, trying direct HTTP: {client_error}")
            
            # Fallback to direct HTTP request
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": texts,
                "model": EMBEDDING_MODEL
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return [item['embedding'] for item in result.get('data', [])]
            else:
                logger.error(f"HTTP request failed: {response.status_code} - {response.text}")
                raise RuntimeError(f"HTTP {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"Failed to get embeddings: {e}")
        raise RuntimeError(f"Embedding generation failed: {e}")

# Upsert chunks to FAISS
async def upsert_chunks_to_faiss(chunks: List[str], doc_id: str) -> List[str]:
    """
    Upsert document chunks to FAISS index with metadata.
    
    Args:
        chunks: List of text chunks
        doc_id: Document identifier
        
    Returns:
        List of vector IDs
    """
    try:
        # Get embeddings for chunks
        embeddings = await get_embeddings(chunks)
        
        # Prepare metadata for each chunk
        metadata = []
        vector_ids = []
        
        for i, chunk in enumerate(chunks):
            metadata.append({
                'text': chunk,
                'doc_id': doc_id,
                'chunk_index': i,
                'chunk_type': 'document_segment'
            })
            vector_ids.append(f"{doc_id}_chunk_{i}")
        
        # Upsert to FAISS
        result_ids = faiss_index.upsert(embeddings, metadata, vector_ids)
        
        logger.info(f"Successfully upserted {len(chunks)} chunks to FAISS for document {doc_id}")
        return result_ids
        
    except Exception as e:
        logger.error(f"FAISS upsert failed: {e}")
        raise RuntimeError(f"FAISS upsert failed: {e}")

# Query FAISS for top_k most similar chunks
async def query_faiss(query: str, top_k: int = 5) -> List[Dict]:
    """
    Query FAISS index for similar document chunks.
    
    Args:
        query: Query text
        top_k: Number of top results to return
        
    Returns:
        List of dictionaries with 'id', 'score', and 'metadata' keys
    """
    try:
        # Get query embedding
        query_embedding = (await get_embeddings([query]))[0]
        
        # Query FAISS index
        results = faiss_index.query(query_embedding, top_k=top_k)
        
        logger.info(f"FAISS query returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"FAISS query failed: {e}")
        raise RuntimeError(f"FAISS query failed: {e}")

# Legacy function names for backward compatibility
async def upsert_chunks_to_pinecone(chunks: List[str], doc_id: str) -> List[str]:
    """Legacy function name - redirects to FAISS implementation."""
    return await upsert_chunks_to_faiss(chunks, doc_id)

async def query_pinecone(query: str, top_k: int = 5) -> List[Dict]:
    """Legacy function name - redirects to FAISS implementation."""
    return await query_faiss(query, top_k)
