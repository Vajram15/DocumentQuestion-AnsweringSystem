"""
Abstract base classes for the system
Follows Dependency Inversion and Interface Segregation principles
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class DocumentProcessor(ABC):
    """
    Abstract base class for document processing
    Defines interface that all processors must implement
    """
    
    @abstractmethod
    async def process(self, content: str) -> List[str]:
        """
        Process document content into chunks
        
        Args:
            content: Raw document content
            
        Returns:
            List of processed text chunks
        """
        pass


class EmbeddingsService(ABC):
    """
    Abstract base class for embeddings generation
    Depends on abstraction, not concrete implementations
    """
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass


class Retriever(ABC):
    """
    Abstract base class for document retrieval
    Single Responsibility: Only handle document retrieval
    """
    
    @abstractmethod
    async def retrieve(self, query: str, k: int = 3, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents/chunks
        
        Args:
            query: Search query
            k: Number of results to retrieve
            document_id: Optional specific document ID
            
        Returns:
            List of relevant document chunks
        """
        pass


class QuestionAnswerer(ABC):
    """
    Abstract base class for question answering
    Highest level abstraction for QA logic
    """
    
    @abstractmethod
    async def answer(self, question: str, document_id: Optional[str] = None, k: int = 3) -> Dict[str, Any]:
        """
        Answer a question based on documents
        
        Args:
            question: User question
            document_id: Optional specific document
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer, sources, and confidence
        """
        pass
