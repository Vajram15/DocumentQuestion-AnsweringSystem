"""
Core module - Contains business logic abstractions and implementations
"""

from src.core.abstractions import (
    DocumentProcessor,
    EmbeddingsService,
    Retriever,
    QuestionAnswerer
)
from src.core.document_processor import LangChainDocumentProcessor
from src.core.embeddings_service import OpenAIEmbeddingsService
from src.core.retriever import InMemoryRetriever

__all__ = [
    "DocumentProcessor",
    "EmbeddingsService",
    "Retriever",
    "QuestionAnswerer",
    "LangChainDocumentProcessor",
    "OpenAIEmbeddingsService",
    "InMemoryRetriever"
]
