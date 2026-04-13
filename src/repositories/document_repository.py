"""
Document repository - Data access layer
Follows Repository Pattern for Single Responsibility
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import json


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


class FileDocumentRepository(IDocumentRepository):
    """
    File-system backed implementation of document repository.
    Saves raw document content to DOCUMENTS_DIR and metadata as JSON.
    Survives server restarts.
    """

    def __init__(self, documents_dir: str = "documents"):
        self.documents_dir = documents_dir
        os.makedirs(documents_dir, exist_ok=True)

    def _meta_path(self, document_id: str) -> str:
        return os.path.join(self.documents_dir, f"{document_id}.json")

    def _content_path(self, document_id: str) -> str:
        return os.path.join(self.documents_dir, f"{document_id}.txt")

    def _load_meta(self, document_id: str) -> Optional[Dict[str, Any]]:
        path = self._meta_path(document_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def save(self, name: str, content: str) -> Dict[str, Any]:
        """Save document content to disk and metadata as JSON."""
        document_id = str(uuid.uuid4())

        # Write raw content
        with open(self._content_path(document_id), "w", encoding="utf-8") as f:
            f.write(content)

        # Write metadata
        metadata = {
            "id": document_id,
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
            "file_path": self._content_path(document_id),
        }
        with open(self._meta_path(document_id), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return metadata

    async def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        return self._load_meta(document_id)

    async def get_all(self) -> List[Dict[str, Any]]:
        results = []
        for filename in os.listdir(self.documents_dir):
            if filename.endswith(".json"):
                doc_id = filename[:-5]
                meta = self._load_meta(doc_id)
                if meta:
                    results.append(meta)
        return results

    async def delete(self, document_id: str) -> bool:
        if not await self.exists(document_id):
            return False
        for path in (self._content_path(document_id), self._meta_path(document_id)):
            if os.path.exists(path):
                os.remove(path)
        return True

    async def exists(self, document_id: str) -> bool:
        return os.path.exists(self._meta_path(document_id))
