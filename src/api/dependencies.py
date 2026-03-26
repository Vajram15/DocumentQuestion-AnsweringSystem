"""
Dependency injection and FastAPI dependencies
Follows Dependency Inversion Principle
"""

from typing import Optional
from fastapi import Depends
from src.config import get_settings, Settings
from src.core import (
    LangChainDocumentProcessor,
    OpenAIEmbeddingsService,
    InMemoryRetriever
)
from src.services import LangChainQAService, DocumentService
from src.repositories import InMemoryDocumentRepository
from src.utils.logger import logger


class DIContainer:
    """
    Dependency Injection Container
    Singleton pattern for managing dependencies
    """
    
    _instance: Optional['DIContainer'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing Dependency Injection Container")
        
        # Settings
        self.settings = get_settings()
        
        # Core services
        self.document_processor = LangChainDocumentProcessor()
        self.embeddings_service = OpenAIEmbeddingsService()
        self.retriever = InMemoryRetriever(self.embeddings_service)
        
        # Repository
        self.repository = InMemoryDocumentRepository()
        
        # Business logic services
        self.qa_service = LangChainQAService(
            retriever=self.retriever,
            document_processor=self.document_processor,
            repository=self.repository
        )
        
        self.document_service = DocumentService(
            repository=self.repository,
            processor=self.document_processor,
            retriever=self.retriever
        )
        
        self._initialized = True
        logger.info("Dependency Injection Container initialized successfully")
    
    @classmethod
    def get_instance(cls) -> 'DIContainer':
        """Get singleton instance"""
        return cls()


# FastAPI dependency functions
def get_di_container() -> DIContainer:
    """Get DI container - Singleton pattern"""
    return DIContainer.get_instance()


async def get_qa_service(container: DIContainer = Depends(get_di_container)) -> LangChainQAService:
    """Dependency: QA Service"""
    return container.qa_service


async def get_document_service(container: DIContainer = Depends(get_di_container)) -> DocumentService:
    """Dependency: Document Service"""
    return container.document_service


async def get_settings_dep(container: DIContainer = Depends(get_di_container)) -> Settings:
    """Dependency: Settings"""
    return container.settings
