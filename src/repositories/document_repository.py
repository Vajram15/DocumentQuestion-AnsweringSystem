"""
Document repository - Data access layer
Follows Repository Pattern for Single Responsibility
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class IDocumentRepository(ABC):
    """Abstract repository interface"""
    
    @abstractmethod
    async def save(self, name: str, content: str) -> Dict[str, Any]:
        """Save document"""
        pass
    
    @abstractmethod
    async def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete document"""
        pass
    
    @abstractmethod
    async def exists(self, document_id: str) -> bool:
        """Check if document exists"""
        pass


class InMemoryDocumentRepository(IDocumentRepository):
    """
    In-memory implementation of document repository
    Single Responsibility: Manage document storage
    """
    
    def __init__(self):
        """Initialize repository"""
        self.documents: Dict[str, Dict[str, Any]] = {}
    
    async def save(self, name: str, content: str) -> Dict[str, Any]:
        """
        Save document to repository
        
        Args:
            name: Document name
            content: Document content
            
        Returns:
            Saved document data
        """
        document_id = str(uuid.uuid4())
        document = {
            "id": document_id,
            "name": name,
            "content": content,
            "created_at": datetime.utcnow()
        }
        self.documents[document_id] = document
        return document
    
    async def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID
        
        Args:
            document_id: Document identifier
            
        Returns:
            Document data or None
        """
        return self.documents.get(document_id)
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all documents
        
        Returns:
            List of documents
        """
        return list(self.documents.values())
    
    async def delete(self, document_id: str) -> bool:
        """
        Delete document
        
        Args:
            document_id: Document to delete
            
        Returns:
            True if successful
        """
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False
    
    async def exists(self, document_id: str) -> bool:
        """
        Check if document exists
        
        Args:
            document_id: Document ID to check
            
        Returns:
            True if exists
        """
        return document_id in self.documents
