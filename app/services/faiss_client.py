import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Optional
import logging
from app.core.config import FAISS_INDEX_PATH, FAISS_DIMENSION

logger = logging.getLogger(__name__)

class FaissIndex:
    """FAISS vector index for local semantic search with metadata storage."""
    
    def __init__(self, dim=None, index_path=None):
        self.dim = dim or FAISS_DIMENSION
        self.index_path = index_path or FAISS_INDEX_PATH
        self.metadata_path = f"{self.index_path}_metadata.pkl"
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dim)  # Inner product for cosine similarity
        
        # Metadata storage
        self.metadata = []
        self.vector_ids = []
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and metadata if available."""
        try:
            if os.path.exists(f"{self.index_path}.index"):
                self.index = faiss.read_index(f"{self.index_path}.index")
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
                
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, 'rb') as f:
                        data = pickle.load(f)
                        self.metadata = data.get('metadata', [])
                        self.vector_ids = data.get('vector_ids', [])
                    logger.info(f"Loaded metadata for {len(self.metadata)} vectors")
        except Exception as e:
            logger.warning(f"Could not load existing index: {e}")
    
    def _save_index(self):
        """Save FAISS index and metadata to disk."""
        try:
            faiss.write_index(self.index, f"{self.index_path}.index")
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'vector_ids': self.vector_ids
                }, f)
            logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def upsert(self, vectors: List[List[float]], metadata: List[Dict], vector_ids: Optional[List[str]] = None):
        """
        Upsert vectors with metadata to FAISS index.
        
        Args:
            vectors: List of embedding vectors
            metadata: List of metadata dictionaries for each vector
            vector_ids: Optional list of vector IDs
        """
        if len(vectors) != len(metadata):
            raise ValueError("Number of vectors must match number of metadata items")
        
        # Convert to numpy array
        vectors_array = np.array(vectors, dtype='float32')
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors_array)
        
        # Add to FAISS index
        self.index.add(vectors_array)
        
        # Store metadata
        self.metadata.extend(metadata)
        
        # Generate or use provided vector IDs
        if vector_ids is None:
            start_id = len(self.vector_ids)
            vector_ids = [f"vec_{start_id + i}" for i in range(len(vectors))]
        
        self.vector_ids.extend(vector_ids)
        
        # Save to disk
        self._save_index()
        
        logger.info(f"Upserted {len(vectors)} vectors to FAISS index")
        return vector_ids
    
    def query(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        Query FAISS index for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with 'id', 'score', and 'metadata' keys
        """
        if self.index.ntotal == 0:
            return []
        
        # Convert to numpy array and normalize
        query_array = np.array([query_vector], dtype='float32')
        faiss.normalize_L2(query_array)
        
        # Search
        scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx != -1 and idx < len(self.metadata):
                results.append({
                    'id': self.vector_ids[idx],
                    'score': float(score),
                    'metadata': self.metadata[idx]
                })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get statistics about the FAISS index."""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dim,
            'metadata_count': len(self.metadata)
        }
    
    def clear(self):
        """Clear the FAISS index and metadata."""
        self.index = faiss.IndexFlatIP(self.dim)
        self.metadata = []
        self.vector_ids = []
        
        # Remove saved files
        for path in [f"{self.index_path}.index", self.metadata_path]:
            if os.path.exists(path):
                os.remove(path)
        
        logger.info("Cleared FAISS index and metadata")

# Global FAISS index instance
faiss_index = FaissIndex() 