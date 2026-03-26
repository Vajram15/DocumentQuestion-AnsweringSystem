"""
Repositories module - Data access layer
"""

from src.repositories.document_repository import (
    IDocumentRepository,
    InMemoryDocumentRepository
)

__all__ = [
    "IDocumentRepository",
    "InMemoryDocumentRepository"
]
