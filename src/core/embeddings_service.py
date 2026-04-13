"""
Embeddings service implementation
Single Responsibility: Generate embeddings for text
"""

from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.core.abstractions import EmbeddingsService
from src.config import get_settings
from src.utils.logger import logger


class OpenAIEmbeddingsService(EmbeddingsService):
    """
    Concrete implementation using HuggingFace embeddings from LangChain Community
    Single Responsibility: Only generate embeddings
    Uses local model - no API key required
    """
    
    def __init__(self, model: str = None):
        """
        Initialize embeddings service
        
        Args:
            model: HuggingFace model name (default: all-MiniLM-L6-v2)
        """
        settings = get_settings()
        # Use HuggingFace model instead of OpenAI
        self.model = model or "all-MiniLM-L6-v2"
        
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name=self.model)
            logger.info(f"Embeddings service initialized with HuggingFace: model={self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace embeddings: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                return []
            
            embedding = self.embeddings.embed_query(text)
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                logger.warning("Empty list provided for embedding")
                return []
            
            embeddings = self.embeddings.embed_documents(texts)
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
