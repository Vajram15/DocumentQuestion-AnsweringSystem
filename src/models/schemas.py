"""
Pydantic schemas for API requests and responses
Follows Interface Segregation Principle with specific models for each use case
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    """Base model for document data"""
    name: str = Field(..., min_length=1, description="Document name")
    content: str = Field(..., min_length=1, description="Document content")


class DocumentCreate(DocumentBase):
    """Model for creating documents"""
    pass


class DocumentResponse(DocumentBase):
    """Model for document responses"""
    id: str = Field(..., description="Document unique identifier")
    created_at: datetime = Field(..., description="Document creation timestamp")
    
    class Config:
        from_attributes = True


class QuestionRequest(BaseModel):
    """Model for question requests"""
    question: str = Field(..., min_length=1, description="User question")
    document_id: Optional[str] = Field(None, description="Specific document to search")
    k: int = Field(default=3, ge=1, le=10, description="Number of retrieved chunks")


class AnswerResponse(BaseModel):
    """Model for answer responses"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    sources: List[str] = Field(default=[], description="Source chunks used")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence score")


class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details")


class HealthResponse(BaseModel):
    """Model for health check response"""
    status: str = Field(default="ok", description="Service status")
    version: str = Field(..., description="API version")
