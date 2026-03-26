# API Specification

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication is required. In production, JWT authentication can be added.

---

## Health Check

### GET /health
Check if the API is running and healthy.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**Status Code:** 200 OK

---

## Documents API

### POST /documents/upload
Upload and process a new document.

**Request Body:**
```json
{
  "name": "document_name.pdf",
  "content": "Full text content of the document..."
}
```

**Response:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "document_name.pdf",
  "chunks_count": 5,
  "status": "success"
}
```

**Status Codes:**
- `201 Created` - Document uploaded successfully
- `400 Bad Request` - Invalid input
- `500 Internal Server Error` - Server error

---

### GET /documents
List all uploaded documents.

**Query Parameters:** None

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "document_name.pdf",
    "content": "Document content...",
    "created_at": "2024-03-26T10:30:00"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

### GET /documents/{document_id}
Get details of a specific document.

**Path Parameters:**
- `document_id` (string, required) - Document unique identifier

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "document_name.pdf",
  "content": "Document content...",
  "created_at": "2024-03-26T10:30:00"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Document not found
- `500 Internal Server Error` - Server error

---

### DELETE /documents/{document_id}
Delete a document and remove it from the vector store.

**Path Parameters:**
- `document_id` (string, required) - Document unique identifier

**Response:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "deleted"
}
```

**Status Codes:**
- `200 OK` - Successfully deleted
- `404 Not Found` - Document not found
- `500 Internal Server Error` - Server error

---

## Question-Answering API

### POST /qa/ask
Ask a question about uploaded documents.

**Request Body:**
```json
{
  "question": "What is the main topic of the document?",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "k": 3
}
```

**Request Fields:**
- `question` (string, required) - The question to ask (min length: 1)
- `document_id` (string, optional) - Specific document ID to search. If not provided, searches all documents
- `k` (integer, optional, default: 3) - Number of relevant chunks to retrieve (1-10)

**Response:**
```json
{
  "question": "What is the main topic of the document?",
  "answer": "The main topic of the document is artificial intelligence and machine learning applications in healthcare...",
  "sources": [
    "550e8400-e29b-41d4-a716-446655440000: Chapter 1 discusses AI applications in healthcare including diagnostics and monitoring...",
    "550e8400-e29b-41d4-a716-446655440000: Section 2.1 explains machine learning models used for disease prediction..."
  ],
  "confidence": 0.87
}
```

**Response Fields:**
- `question` (string) - The original question
- `answer` (string) - Generated answer based on document content
- `sources` (array of strings) - List of source chunks used to generate the answer
- `confidence` (number, 0-1) - Confidence score based on semantic similarity

**Status Codes:**
- `200 OK` - Successfully generated answer
- `400 Bad Request` - Invalid input (empty question, invalid k value)
- `500 Internal Server Error` - Server error during processing

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "details": "Optional detailed error information"
}
```

### Common Error Scenarios

#### Empty Question
```
Request: {"question": ""}
Response: 400 Bad Request
{
  "error": "Question cannot be empty",
  "details": null
}
```

#### Document Not Found
```
Request: GET /documents/invalid-id
Response: 404 Not Found
{
  "error": "Document not found",
  "details": null
}
```

#### No Relevant Content
```
Request: {"question": "Something unrelated to documents"}
Response: 200 OK
{
  "question": "Something unrelated to documents",
  "answer": "I could not find any relevant information to answer your question.",
  "sources": [],
  "confidence": 0.0
}
```

#### Server Error
```
Response: 500 Internal Server Error
{
  "error": "Internal server error",
  "details": "Detailed error message for debugging"
}
```

---

## Request/Response Examples

### Example 1: Upload Document and Ask Question

**Step 1: Upload Document**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ai_guide.pdf",
    "content": "Artificial Intelligence (AI) is transforming industries worldwide. Machine learning, a subset of AI, enables systems to learn from data. Deep learning uses neural networks for complex pattern recognition. Natural Language Processing (NLP) allows computers to understand human language. Computer vision enables image and video analysis. These technologies are revolutionizing healthcare, finance, and transportation."
  }'
```

**Response:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ai_guide.pdf",
  "chunks_count": 2,
  "status": "success"
}
```

**Step 2: Ask Question**
```bash
curl -X POST "http://localhost:8000/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "k": 2
  }'
```

**Response:**
```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is a subset of AI that enables systems to learn from data without being explicitly programmed.",
  "sources": [
    "550e8400-e29b-41d4-a716-446655440000: Machine learning, a subset of AI, enables systems to learn from data...",
    "550e8400-e29b-41d4-a716-446655440000: Deep learning uses neural networks for complex pattern recognition..."
  ],
  "confidence": 0.94
}
```

---

## Rate Limiting
Currently not implemented. Can be added using FastAPI middleware.

## Pagination
Currently not implemented for document listing. Can be added for large datasets.

## Versioning
No API versioning currently. Can be added as `/v1/`, `/v2/` paths if needed.

## CORS
CORS is enabled for all origins (`*`). Configure in production for specific domains.

---

## Future Enhancements

- [ ] API authentication (JWT)
- [ ] Rate limiting
- [ ] Request/response logging
- [ ] Batch document upload
- [ ] Advanced filtering for document list
- [ ] Document metadata (tags, categories)
- [ ] Chat history/conversation support
- [ ] API versioning
- [ ] OpenAPI/Swagger documentation improvements
