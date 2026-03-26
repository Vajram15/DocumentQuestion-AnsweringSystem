"""
Unit tests for QA system
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.services.qa_service import LangChainQAService
from src.services.document_service import DocumentService
from src.core.document_processor import LangChainDocumentProcessor


@pytest.fixture
def mock_retriever():
    """Mock retriever fixture"""
    retriever = AsyncMock()
    retriever.retrieve = AsyncMock(return_value=[
        {
            "document_id": "doc1",
            "content": "Sample content about AI",
            "score": 0.95
        }
    ])
    return retriever


@pytest.fixture
def mock_processor():
    """Mock processor fixture"""
    processor = AsyncMock()
    processor.process = AsyncMock(return_value=["chunk1", "chunk2", "chunk3"])
    return processor


@pytest.fixture
def mock_repository():
    """Mock repository fixture"""
    repository = AsyncMock()
    repository.save = AsyncMock(return_value={"id": "doc1", "name": "test", "content": "content"})
    repository.get = AsyncMock(return_value={"id": "doc1", "name": "test", "content": "content"})
    repository.get_all = AsyncMock(return_value=[{"id": "doc1", "name": "test"}])
    repository.delete = AsyncMock(return_value=True)
    repository.exists = AsyncMock(return_value=True)
    return repository


@pytest.mark.asyncio
async def test_document_upload(mock_repository, mock_processor):
    """Test document upload functionality"""
    mock_retriever = AsyncMock()
    
    service = DocumentService(
        repository=mock_repository,
        processor=mock_processor,
        retriever=mock_retriever
    )
    
    result = await service.upload_document("test.pdf", "Test content")
    
    assert result["status"] == "success"
    assert "document_id" in result
    assert result["chunks_count"] == 3


@pytest.mark.asyncio
async def test_document_delete(mock_repository, mock_processor):
    """Test document deletion"""
    mock_retriever = AsyncMock()
    
    service = DocumentService(
        repository=mock_repository,
        processor=mock_processor,
        retriever=mock_retriever
    )
    
    result = await service.delete_document("doc1")
    
    assert result["status"] == "deleted"
    assert result["document_id"] == "doc1"


@pytest.mark.asyncio
async def test_question_answering(mock_retriever, mock_processor, mock_repository):
    """Test question answering functionality"""
    with patch('src.services.qa_service.ChatOpenAI'):
        qa_service = LangChainQAService(
            retriever=mock_retriever,
            document_processor=mock_processor,
            repository=mock_repository
        )
        
        # Mock the chain
        qa_service.chain = AsyncMock()
        qa_service.chain.arun = AsyncMock(return_value="AI is artificial intelligence")
        
        result = await qa_service.answer("What is AI?")
        
        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert result["question"] == "What is AI?"
