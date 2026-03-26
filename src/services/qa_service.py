"""
Question-Answering service
Core business logic for answering questions
Follows Single Responsibility Principle
"""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from src.core.abstractions import QuestionAnswerer, Retriever, DocumentProcessor
from src.repositories.document_repository import IDocumentRepository
from src.config import get_settings
from src.utils.logger import logger


class LangChainQAService(QuestionAnswerer):
    """
    Question answering service using LangChain
    Single Responsibility: Generate answers from retrieved documents
    Depends on abstractions (Dependency Inversion Principle)
    """
    
    def __init__(
        self,
        retriever: Retriever,
        document_processor: DocumentProcessor,
        repository: IDocumentRepository
    ):
        """
        Initialize QA service with dependencies
        
        Args:
            retriever: Document retriever
            document_processor: Document processor
            repository: Document repository
        """
        settings = get_settings()
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.retriever = retriever
        self.document_processor = document_processor
        self.repository = repository
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant. Answer the question based on the provided context.
            
Context:
{context}

Question: {question}

Answer: Provide a clear, concise answer based on the context. If the context doesn't contain relevant information, say so."""
        )
        
        # Create chain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        logger.info("QA Service initialized")
    
    async def answer(
        self,
        question: str,
        document_id: Optional[str] = None,
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Answer a question based on documents
        
        Args:
            question: User question
            document_id: Optional specific document
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer, sources, and confidence
        """
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")
            
            # Retrieve relevant chunks
            logger.info(f"Retrieving chunks for question: {question}")
            retrieved_chunks = await self.retriever.retrieve(question, k=k, document_id=document_id)
            
            if not retrieved_chunks:
                logger.warning("No relevant chunks found")
                return {
                    "question": question,
                    "answer": "I could not find any relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Prepare context
            context = "\n".join([f"[{chunk['document_id']}] {chunk['content']}" for chunk in retrieved_chunks])
            
            # Generate answer
            logger.info("Generating answer")
            response = await self.chain.arun(context=context, question=question)
            
            # Calculate confidence as average score of retrieved chunks
            confidence = sum(chunk["score"] for chunk in retrieved_chunks) / len(retrieved_chunks)
            
            return {
                "question": question,
                "answer": response.strip(),
                "sources": [f"{chunk['document_id']}: {chunk['content'][:100]}..." for chunk in retrieved_chunks],
                "confidence": float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
