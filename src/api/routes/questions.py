"""
Question-Answering API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from src.models import QuestionRequest, AnswerResponse
from src.services import LangChainQAService
from src.api.dependencies import get_qa_service
from src.utils.logger import logger

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    qa_service: LangChainQAService = Depends(get_qa_service)
) -> AnswerResponse:
    """
    Ask a question about documents
    
    Args:
        request: Question request with question text and optional document ID
        qa_service: Injected QA service
        
    Returns:
        Answer with sources and confidence score
    """
    try:
        result = await qa_service.answer(
            question=request.question,
            document_id=request.document_id,
            k=request.k
        )
        return AnswerResponse(**result)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Question answering error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing question")
