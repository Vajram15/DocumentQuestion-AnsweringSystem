"""
Document management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from src.models import DocumentCreate, DocumentResponse
from src.services import DocumentService
from src.api.dependencies import get_document_service
from src.utils.logger import logger
from pypdf import PdfReader
import io

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=None, status_code=status.HTTP_201_CREATED)
async def upload_document(
    document: DocumentCreate,
    document_service: DocumentService = Depends(get_document_service)
) -> dict:
    """
    Upload and process a new document
    
    Args:
        document: Document data (name and content)
        document_service: Injected document service
        
    Returns:
        Upload result with document ID
    """
    try:
        result = await document_service.upload_document(document.name, document.content)
        return result
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading document")


@router.post("/upload-pdf", response_model=None, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service)
) -> dict:
    """
    Upload and process a PDF document
    
    Args:
        file: PDF file to upload
        document_service: Injected document service
        
    Returns:
        Upload result with document ID
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise ValueError("File must be a PDF document")
        
        # Read PDF content
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        
        # Extract text from all pages
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        if not text_content.strip():
            raise ValueError("PDF contains no readable text")
        
        # Extract filename without extension
        doc_name = file.filename.replace('.pdf', '')
        
        # Upload using document service
        result = await document_service.upload_document(doc_name, text_content)
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"PDF upload error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading PDF: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:
    """
    Get document details
    
    Args:
        document_id: Document ID
        document_service: Injected document service
        
    Returns:
        Document details
    """
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return DocumentResponse(**document)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving document")


@router.get("/", response_model=list)
async def list_documents(
    document_service: DocumentService = Depends(get_document_service)
) -> list:
    """
    List all documents
    
    Args:
        document_service: Injected document service
        
    Returns:
        List of documents
    """
    try:
        documents = await document_service.list_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing documents")


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
) -> dict:
    """
    Delete a document
    
    Args:
        document_id: Document ID to delete
        document_service: Injected document service
        
    Returns:
        Deletion confirmation
    """
    try:
        result = await document_service.delete_document(document_id)
        return result
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Deletion error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting document")
