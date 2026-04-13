"""
Repositories module - Data access layer
"""

from src.repositories.document_repository import (
    IDocumentRepository,
    InMemoryDocumentRepository,
    FileDocumentRepository
)

__all__ = [
    "IDocumentRepository",
    "InMemoryDocumentRepository",
    "FileDocumentRepository"
]
