"""
Question-Answering service
Core business logic for answering questions
Follows Single Responsibility Principle
"""

from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
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
        
        self.retriever = retriever
        self.document_processor = document_processor
        self.repository = repository
        self.chain = None
        self.k = 3  # Default retrieval count
        
        # Try to initialize ChatGroq LLM
        try:
            groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
            logger.debug(f"[GROQ] API key loaded: {'***' + groq_api_key[-10:] if groq_api_key else 'NONE'}")
            
            if not groq_api_key or groq_api_key.strip() == "":
                logger.warning("Groq API key not configured. QA will use simple retrieval without LLM synthesis.")
                self.llm = None
            else:
                logger.debug(f"[GROQ] Initializing ChatGroq with key: {groq_api_key[:20]}...")
                self.llm = ChatGroq(
                    model=settings.GROQ_MODEL,
                    temperature=0.3,
                    api_key=groq_api_key
                )
                logger.info(f"[GROQ] ChatGroq initialized successfully")
                
                # Create focused prompt template for concise answers
                prompt_template = PromptTemplate(
                    input_variables=["context", "question"],
                    template="""You are a helpful assistant that answers questions based on the provided context. 

IMPORTANT: Provide a concise, specific answer to the question using only the information from the context. Do not copy the entire context or repeat unnecessary information. Answer directly and briefly.

Context:
{context}

Question: {question}

Answer:"""
                )
                
                # Create chain
                self.chain = LLMChain(llm=self.llm, prompt=prompt_template)
                logger.info("QA Service initialized with Groq LLM")
        except Exception as e:
            logger.error(f"Failed to initialize Groq LLM: {str(e)}", exc_info=True)
            self.llm = None
            self.chain = None
    
    async def answer(
        self,
        question: str,
        document_id: Optional[str] = None,
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Answer a question based on documents using semantic search and LLM
        
        Args:
            question: User question
            document_id: Optional specific document to search in
            k: Number of top chunks to retrieve (default: 3)
            
        Returns:
            Dictionary with answer, sources, and confidence
        """
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")
            
            # Retrieve top k=3 relevant chunks with similarity search
            logger.info(f"Retrieving top {k} chunks for question: {question}")
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
            
            # Generate answer - use LLM if available
            if self.chain:
                logger.info("Generating answer with Groq LLM")
                response = await self.chain.arun(context=context, question=question)
                answer = response.strip()
            else:
                logger.info("Using retrieval-based answer (no LLM available)")
                answer = f"Based on the documents, here is relevant information:\n\n{context}"
            
            # Calculate confidence as average score of retrieved chunks
            # Note: FAISS returns distance (lower is better), so invert
            confidence = 1.0 / (1.0 + (sum(chunk["score"] for chunk in retrieved_chunks) / len(retrieved_chunks)))
            
            return {
                "question": question,
                "answer": answer,
                "sources": [f"{chunk['document_id']}: {chunk['content'][:100]}..." for chunk in retrieved_chunks],
                "confidence": float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
