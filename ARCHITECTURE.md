# System Architecture

## Overview

This Document Question-Answering System is built using **FastAPI**, **LangChain**, and follows **SOLID principles** with a modular, layered architecture.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│          FastAPI REST API               │
│     (routes/documents, /routes/qa)      │
├─────────────────────────────────────────┤
│         Services Layer                  │
│  (DocumentService, LangChainQAService)  │
├─────────────────────────────────────────┤
│      Core Business Logic                │
│ (Abstractions + Implementations)        │
├─────────────────────────────────────────┤
│      Data Access Layer                  │
│      (Repositories)                     │
├─────────────────────────────────────────┤
│      External Services Integration      │
│  (OpenAI, LangChain, Vector Store)      │
└─────────────────────────────────────────┘
```

## SOLID Principles Implementation

### 1. **Single Responsibility Principle (SRP)**

Each class has one reason to change:

- **LangChainDocumentProcessor**: Only splits documents into chunks
- **OpenAIEmbeddingsService**: Only generates embeddings
- **InMemoryRetriever**: Only retrieves relevant chunks
- **LangChainQAService**: Only generates answers from context
- **DocumentService**: Only manages document lifecycle
- **InMemoryDocumentRepository**: Only manages document storage

### 2. **Open/Closed Principle (OCP)**

System is open for extension, closed for modification:

```python
# Abstract base classes for extension
class DocumentProcessor(ABC)
class EmbeddingsService(ABC)
class Retriever(ABC)
class QuestionAnswerer(ABC)
```

New implementations can be added without modifying existing code.

### 3. **Liskov Substitution Principle (LSP)**

Concrete implementations can substitute their abstractions:

```python
# All processors implement the same interface
processor = LangChainDocumentProcessor()  # Can be swapped with other implementations

# All embeddings services implement the same interface
embeddings = OpenAIEmbeddingsService()  # Can be replaced with HuggingFace, etc.
```

### 4. **Interface Segregation Principle (ISP)**

Specific interfaces for specific needs:

```python
# Instead of one large interface, separate concerns:
class EmbeddingsService(ABC):
    async def embed_text(self, text: str) -> List[float]
    async def embed_texts(self, texts: List[str]) -> List[List[float]]

class Retriever(ABC):
    async def retrieve(self, query: str, k: int) -> List[Dict]
```

Pydantic schemas are also segregated:

```python
# Specific schemas for specific use cases
class DocumentCreate(BaseModel)
class QuestionRequest(BaseModel)
class AnswerResponse(BaseModel)
```

### 5. **Dependency Inversion Principle (DIP)**

High-level modules depend on abstractions, not low-level modules:

```python
# Services depend on abstractions
class LangChainQAService:
    def __init__(
        self,
        retriever: Retriever,  # Abstraction
        document_processor: DocumentProcessor,  # Abstraction
        repository: IDocumentRepository  # Abstraction
    ):
        # Implementation details are injected
```

## Project Structure

```
src/
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration management
├── core/                       # Core business logic
│   ├── abstractions.py        # Abstract base classes
│   ├── document_processor.py  # Document processing
│   ├── embeddings_service.py  # Embeddings generation
│   └── retriever.py           # Document retrieval
├── services/                   # Business logic services
│   ├── qa_service.py          # Question answering
│   └── document_service.py    # Document management
├── models/                     # Data schemas
│   └── schemas.py             # Pydantic models
├── api/                        # REST API
│   ├── dependencies.py        # Dependency injection
│   ├── routes/
│   │   ├── documents.py       # Document endpoints
│   │   └── questions.py       # QA endpoints
├── repositories/              # Data access layer
│   └── document_repository.py
├── utils/                      # Utilities
│   └── logger.py              # Logging
└── tests/                      # Tests
    └── test_qa.py             # Unit tests
```

## Dependency Injection Pattern

The system uses a **Singleton DI Container** pattern:

```python
class DIContainer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize all dependencies
        return cls._instance
```

### Benefits:
- Single instance of all services
- Centralized dependency management
- Easy to mock for testing
- Follows DIP principle

## Data Flow

### Document Upload Flow

```
1. User uploads document
   ↓
2. DocumentService.upload_document()
   ↓
3. Repository.save() - Store document metadata
   ↓
4. DocumentProcessor.process() - Split into chunks
   ↓
5. EmbeddingsService.embed_texts() - Generate embeddings
   ↓
6. Retriever.add_document() - Store in vector store
```

### Question Answering Flow

```
1. User asks question
   ↓
2. LangChainQAService.answer()
   ↓
3. Retriever.retrieve() - Find relevant chunks
   ↓
4. LLM generates answer from context
   ↓
5. Return answer with sources and confidence
```

## Configuration Management

Uses **Pydantic Settings** for environment-based configuration:

```python
- Load from environment variables
- Centralized configuration
- Type-safe defaults
- Easy to override for different environments
```

## Error Handling

- **Structured exceptions** at service layer
- **HTTPException** for API responses
- **Logging** at all critical points
- **Graceful degradation**

## Testing

- **Unit tests** with async support
- **Mocking** of external services
- **Fixture-based** test setup
- **AsyncMock** for async operations

## Extensibility

### Adding a New Document Processor

```python
class CustomDocumentProcessor(DocumentProcessor):
    async def process(self, content: str) -> List[str]:
        # Custom implementation
        pass
```

### Adding a New Embeddings Service

```python
class HuggingFaceEmbeddings(EmbeddingsService):
    async def embed_text(self, text: str) -> List[float]:
        # Custom implementation
        pass
```

### Adding a New Retriever

```python
class VectorDBRetriever(Retriever):
    async def retrieve(self, query: str, k: int = 3, document_id: Optional[str] = None) -> List[Dict]:
        # Custom implementation using external vector DB
        pass
```

## Environment Setup

1. Copy `.env.example` to `.env`
2. Fill in required values (especially `OPENAI_API_KEY`)
3. Activate virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python -m uvicorn src.main:app --reload`

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents` - List all documents
- `GET /documents/{document_id}` - Get document details
- `DELETE /documents/{document_id}` - Delete document

### Question Answering
- `POST /qa/ask` - Ask a question

## Future Enhancements

1. **Persistent Storage**: Replace in-memory with PostgreSQL/MongoDB
2. **Vector Database**: Integration with Pinecone/Weaviate/Qdrant
3. **Authentication**: JWT-based API authentication
4. **Caching**: Redis for caching embeddings
5. **Batch Processing**: Async task queue (Celery)
6. **Advanced Retrieval**: Hybrid search (BM25 + semantic)
7. **Multi-LLM Support**: Support for multiple LLM providers
8. **Model Fine-tuning**: Custom fine-tuned models
