"""
Retriever implementation using LangChain Community FAISS vector store
Single Responsibility: Retrieve relevant documents using vector similarity
"""

from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from src.core.abstractions import Retriever, EmbeddingsService
from src.utils.logger import logger
import os


class InMemoryRetriever(Retriever):
    """
    Vector store retriever using LangChain Community FAISS
    Uses semantic similarity for retrieval
    Single Responsibility: Only retrieves documents
    """
    
    def __init__(self, embeddings_service: EmbeddingsService, vector_store_dir: str = "vector_store"):
        """
        Initialize retriever with embeddings service
        
        Args:
            embeddings_service: Service for generating embeddings
            vector_store_dir: Directory to persist vector store
        """
        self.embeddings_service = embeddings_service
        self.vector_store_dir = vector_store_dir
        self.document_metadata = {}  # Track document IDs
        
        # Try to load existing vector store
        if os.path.exists(self.vector_store_dir):
            try:
                logger.info(f"Loading existing FAISS vector store from {self.vector_store_dir}")
                self.vectorstore = FAISS.load_local(self.vector_store_dir, self.embeddings_service.embeddings)
                logger.info("FAISS vector store loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load existing vector store: {str(e)}. Starting fresh.")
                self.vectorstore = None
        else:
            self.vectorstore = None
            logger.info("No existing vector store found. Starting fresh.")
        
        logger.info("FAISS retriever initialized")
    
    async def add_document(self, document_id: str, chunks: List[str]) -> None:
        """
        Add document chunks to FAISS vector store
        
        Args:
            document_id: Unique document identifier
            chunks: List of text chunks
        """
        try:
            logger.debug(f"[FAISS] Starting add_document: {document_id}, chunks_count={len(chunks)}")
            
            # Create Document objects with metadata
            documents = [
                Document(page_content=chunk, metadata={"document_id": document_id, "chunk_index": i})
                for i, chunk in enumerate(chunks)
            ]
            
            # Test: Get embedding for first chunk to verify embeddings work
            if chunks:
                test_embedding = await self.embeddings_service.embed_text(chunks[0][:50])
                logger.debug(f"[FAISS] Test embedding for first chunk: dimension={len(test_embedding)}")
            
            # Create or update vectorstore
            logger.debug(f"[FAISS] Creating/updating vectorstore. Current state: {'initialized' if self.vectorstore else 'None'}")
            if self.vectorstore is None:
                logger.debug(f"[FAISS] Initializing new FAISS vectorstore with {len(documents)} documents")
                self.vectorstore = FAISS.from_documents(
                    documents, 
                    self.embeddings_service.embeddings
                )
                logger.debug(f"[FAISS] FAISS vectorstore initialized: {self.vectorstore}")
            else:
                logger.debug(f"[FAISS] Adding {len(documents)} documents to existing vectorstore")
                self.vectorstore.add_documents(documents)
            
            self.document_metadata[document_id] = len(chunks)
            logger.info(f"Added document {document_id} with {len(chunks)} chunks to FAISS")
            
            # Save vector store to disk
            try:
                os.makedirs(self.vector_store_dir, exist_ok=True)
                self.vectorstore.save_local(self.vector_store_dir)
                logger.debug(f"Vector store saved to {self.vector_store_dir}")
            except Exception as e:
                logger.error(f"Failed to save vector store: {str(e)}")
            
            logger.debug(f"[FAISS] Document added successfully. Vectorstore ID: {id(self.vectorstore)}")
            
        except Exception as e:
            logger.error(f"Error adding document to FAISS: {str(e)}", exc_info=True)
            raise
    
    async def retrieve(
        self, 
        query: str, 
        k: int = 3, 
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using semantic similarity from FAISS
        
        Args:
            query: Search query
            k: Number of results to retrieve
            document_id: Optional specific document ID
            
        Returns:
            List of relevant chunks with scores
        """
        try:
            logger.debug(f"[FAISS] Starting retrieve: query_len={len(query)}, k={k}, document_id={document_id}")
            
            if not query or not query.strip():
                logger.warning("Empty query provided for retrieval")
                return []
            
            if self.vectorstore is None:
                logger.warning("[FAISS] No documents in vector store (vectorstore is None)")
                logger.debug(f"[FAISS] Document metadata: {self.document_metadata}")
                return []
            
            logger.debug(f"[FAISS] Vectorstore available. ID: {id(self.vectorstore)}")
            logger.debug(f"[FAISS] Document metadata in retriever: {self.document_metadata}")
            
            # Embed the query
            logger.debug(f"[FAISS] Embedding query...")
            query_embedding = await self.embeddings_service.embed_text(query)
            logger.debug(f"[FAISS] Query embedding dimension: {len(query_embedding)}")
            
            # Search with similarity scores
            logger.debug(f"[FAISS] Searching FAISS with k={k}...")
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.debug(f"[FAISS] FAISS returned {len(docs_with_scores)} results")
            
            if not docs_with_scores:
                logger.warning("[FAISS] FAISS returned no results")
                return []
            
            # Log raw results
            for i, (doc, score) in enumerate(docs_with_scores):
                logger.debug(f"[FAISS] Result {i}: score={score}, content_len={len(doc.page_content)}, metadata={doc.metadata}")
            
            results = []
            for doc, score in docs_with_scores:
                # Filter by document_id if specified
                doc_id = doc.metadata.get("document_id")
                if document_id and doc_id != document_id:
                    logger.debug(f"[FAISS] Filtering out doc {doc_id} (looking for {document_id})")
                    continue
                
                results.append({
                    "document_id": doc_id,
                    "content": doc.page_content,
                    "score": float(score)  # FAISS returns distance, lower is better
                })
            
            logger.info(f"Retrieved {len(results)} chunks for query from FAISS")
            logger.debug(f"[FAISS] Final results count: {len(results)}, filtered_out: {len(docs_with_scores) - len(results)}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents from FAISS: {str(e)}", exc_info=True)
            raise
    
    async def remove_document(self, document_id: str) -> None:
        """
        Remove document from FAISS vector store
        
        Args:
            document_id: Document to remove
        """
        try:
            if document_id in self.document_metadata:
                # FAISS doesn't support deletion efficiently
                # Rebuild vectorstore without this document
                if self.vectorstore:
                    # This is a workaround - mark as deleted
                    logger.warning(f"Document {document_id} marked for removal (full rebuild recommended)")
                    del self.document_metadata[document_id]
            
        except Exception as e:
            logger.error(f"Error removing document from FAISS: {str(e)}")
            raise
