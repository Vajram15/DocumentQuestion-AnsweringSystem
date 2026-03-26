"""
Retriever implementation using in-memory storage
Single Responsibility: Retrieve relevant documents
"""

from typing import List, Dict, Any, Optional
from src.core.abstractions import Retriever, EmbeddingsService
from src.utils.logger import logger
import numpy as np


class InMemoryRetriever(Retriever):
    """
    In-memory vector store and retriever
    Uses cosine similarity for retrieval
    Single Responsibility: Only retrieves documents
    """
    
    def __init__(self, embeddings_service: EmbeddingsService):
        """
        Initialize retriever with embeddings service
        
        Args:
            embeddings_service: Service for generating embeddings
        """
        self.embeddings_service = embeddings_service
        self.store: Dict[str, Dict[str, Any]] = {}  # {doc_id: {chunks: [], embeddings: []}}
        logger.info("In-memory retriever initialized")
    
    async def add_document(self, document_id: str, chunks: List[str]) -> None:
        """
        Add document chunks to store
        
        Args:
            document_id: Unique document identifier
            chunks: List of text chunks
        """
        try:
            embeddings = await self.embeddings_service.embed_texts(chunks)
            self.store[document_id] = {
                "chunks": chunks,
                "embeddings": embeddings
            }
            logger.info(f"Added document {document_id} with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            raise
    
    async def retrieve(
        self, 
        query: str, 
        k: int = 3, 
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using semantic similarity
        
        Args:
            query: Search query
            k: Number of results to retrieve
            document_id: Optional specific document ID
            
        Returns:
            List of relevant chunks with scores
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty query provided for retrieval")
                return []
            
            # Generate query embedding
            query_embedding = await self.embeddings_service.embed_text(query)
            query_embedding = np.array(query_embedding)
            
            results = []
            
            # Select which documents to search
            docs_to_search = {document_id: self.store[document_id]} if document_id else self.store
            
            # Search through documents
            for doc_id, doc_data in docs_to_search.items():
                chunks = doc_data["chunks"]
                embeddings = np.array(doc_data["embeddings"])
                
                # Calculate cosine similarity
                similarities = np.dot(embeddings, query_embedding) / (
                    np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
                )
                
                # Get top-k results
                top_indices = np.argsort(similarities)[::-1][:k]
                
                for idx in top_indices:
                    results.append({
                        "document_id": doc_id,
                        "content": chunks[idx],
                        "score": float(similarities[idx])
                    })
            
            # Sort by score and return top-k
            results = sorted(results, key=lambda x: x["score"], reverse=True)[:k]
            logger.info(f"Retrieved {len(results)} chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    async def remove_document(self, document_id: str) -> None:
        """
        Remove document from store
        
        Args:
            document_id: Document to remove
        """
        if document_id in self.store:
            del self.store[document_id]
            logger.info(f"Removed document {document_id}")
