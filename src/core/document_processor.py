"""
Document processor implementation
Single Responsibility: Process raw documents into chunks
"""

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.core.abstractions import DocumentProcessor
from src.config import get_settings
from src.utils.logger import logger


class LangChainDocumentProcessor(DocumentProcessor):
    """
    Concrete implementation using LangChain's text splitter
    Single Responsibility: Only chunks documents
    """
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize processor with configurable chunk parameters
        
        Args:
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        """
        settings = get_settings()
        self.chunk_size = chunk_size or settings.MAX_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        logger.info(f"Document processor initialized: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    async def process(self, content: str) -> List[str]:
        """
        Process document content into chunks
        
        Args:
            content: Raw document content
            
        Returns:
            List of text chunks
        """
        try:
            if not content or not content.strip():
                logger.warning("Empty content provided for processing")
                return []
            
            chunks = self.splitter.split_text(content)
            logger.info(f"Document processed into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
