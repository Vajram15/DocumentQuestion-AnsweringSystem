"""
Document service
Handles document management operations
Single Responsibility: Manage document lifecycle
"""

from typing import Dict, Any, Optional, List
from src.core.abstractions import DocumentProcessor
from src.core.retriever import InMemoryRetriever
from src.repositories.document_repository import IDocumentRepository
from src.utils.logger import logger


class DocumentService:
    """
    Document management service
    Single Responsibility: Manage documents (upload, delete, list)
    Follows Dependency Inversion: Works with abstractions
    """
    
    def __init__(
        self,
        repository: IDocumentRepository,
        processor: DocumentProcessor,
        retriever: InMemoryRetriever
    ):
        """
        Initialize document service
        
        Args:
            repository: Document repository
            processor: Document processor
            retriever: Vector store retriever
        """
        self.repository = repository
        self.processor = processor
        self.retriever = retriever
        logger.info("Document Service initialized")
    
    async def upload_document(self, name: str, content: str) -> Dict[str, Any]:
        """
        Upload and process a document
        
        Args:
            name: Document name
            content: Document content
            
        Returns:
            Upload result with document ID
        """
        try:
            if not name or not content:
                raise ValueError("Document name and content are required")
            
            logger.info(f"Uploading document: {name}")
            
            # Save document to repository
            document = await self.repository.save(name, content)
            document_id = document["id"]
            
            # Process document into chunks
            chunks = await self.processor.process(content)
            
            # Add to retriever
            await self.retriever.add_document(document_id, chunks)
            
            logger.info(f"Document {document_id} uploaded successfully with {len(chunks)} chunks")
            
            return {
                "document_id": document_id,
                "name": name,
                "chunks_count": len(chunks),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document
        
        Args:
            document_id: Document to delete
            
        Returns:
            Deletion result
        """
        try:
            logger.info(f"Deleting document: {document_id}")
            
            exists = await self.repository.exists(document_id)
            if not exists:
                raise ValueError(f"Document {document_id} not found")
            
            # Delete from repository
            await self.repository.delete(document_id)
            
            # Delete from retriever
            await self.retriever.remove_document(document_id)
            
            logger.info(f"Document {document_id} deleted successfully")
            
            return {
                "document_id": document_id,
                "status": "deleted"
            }
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document details
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data
        """
        try:
            logger.debug(f"Retrieving document: {document_id}")
            return await self.repository.get(document_id)
            
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            raise
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents
        
        Returns:
            List of documents
        """
        try:
            logger.debug("Listing all documents")
            return await self.repository.get_all()
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
