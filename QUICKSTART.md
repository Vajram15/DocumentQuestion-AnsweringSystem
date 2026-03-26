# Quick Start Guide

## Installation

### 1. Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key (from https://platform.openai.com/api-keys)

### 2. Setup Virtual Environment

```bash
# The virtual environment was already created as 'doc_env'
# Activate it:
.\doc_env\Scripts\Activate.ps1  # On Windows
source doc_env/bin/activate      # On macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

## Running the Application

### Start the Server

```bash
# From project root directory
python -m uvicorn src.main:app --reload

# Or use the uvicorn command directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Usage Examples

### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sample.pdf",
    "content": "Your document content here..."
  }'
```

**Response:**
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "sample.pdf",
  "chunks_count": 5,
  "status": "success"
}
```

### 2. List Documents

```bash
curl "http://localhost:8000/documents/"
```

### 3. Ask a Question

```bash
curl -X POST "http://localhost:8000/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "k": 3,
    "document_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

**Response:**
```json
{
  "question": "What is the main topic?",
  "answer": "The main topic is...",
  "sources": [
    "123e4567-e89b-12d3-a456-426614174000: First relevant chunk...",
    "123e4567-e89b-12d3-a456-426614174000: Second relevant chunk..."
  ],
  "confidence": 0.92
}
```

### 4. Get Document Details

```bash
curl "http://localhost:8000/documents/123e4567-e89b-12d3-a456-426614174000"
```

### 5. Delete Document

```bash
curl -X DELETE "http://localhost:8000/documents/123e4567-e89b-12d3-a456-426614174000"
```

## Using Python Requests Library

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Upload document
document_data = {
    "name": "my_document.txt",
    "content": "This is the content of my document..."
}
response = requests.post(f"{BASE_URL}/documents/upload", json=document_data)
doc_id = response.json()["document_id"]

# Ask question
question_data = {
    "question": "What is this document about?",
    "document_id": doc_id,
    "k": 3
}
response = requests.post(f"{BASE_URL}/qa/ask", json=question_data)
answer = response.json()

print(f"Answer: {answer['answer']}")
print(f"Confidence: {answer['confidence']}")
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest src/tests/

# Run with coverage
pytest --cov=src src/tests/
```

## Project Structure Overview

```
DocumentQuestion-AnsweringSystem/
├── src/                          # Main application code
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration
│   ├── core/                     # Business logic abstractions
│   ├── services/                 # Service implementations
│   ├── models/                   # Data schemas
│   ├── api/                      # REST API endpoints
│   ├── repositories/             # Data access layer
│   ├── utils/                    # Utility functions
│   └── tests/                    # Unit tests
├── requirements.txt              # Python dependencies
├── README.md                     # Project overview
├── ARCHITECTURE.md               # Detailed architecture
├── QUICKSTART.md                 # This file
├── .env.example                  # Example environment configuration
└── .gitignore                    # Git ignore rules
```

## Configuration Options

Edit `.env` file to customize:

```
# OpenAI Settings
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Document Processing
MAX_CHUNK_SIZE=1000              # Characters per chunk
CHUNK_OVERLAP=100                # Overlap between chunks

# Retrieval
EMBEDDINGS_MODEL=text-embedding-3-small

# API
API_PORT=8000
API_HOST=0.0.0.0
```

## Troubleshooting

### Issue: "OPENAI_API_KEY environment variable not set"

**Solution:**
1. Create `.env` file in project root
2. Add `OPENAI_API_KEY=your_key_here`
3. Restart the application

### Issue: Module not found errors

**Solution:**
```bash
# Ensure virtual environment is activated
.\doc_env\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port already in use

**Solution:**
```bash
# Use a different port
uvicorn src.main:app --port 8001
```

## Next Steps

1. **Read ARCHITECTURE.md** - Understand the system design
2. **Explore API docs** - Visit http://localhost:8000/docs
3. **Review code** - Check implementations in `src/core/` and `src/services/`
4. **Extend system** - Add custom processors, embeddings services, or retrievers
5. **Deploy** - Deploy to production using Docker or cloud platforms

## SOLID Principles

This system is built following SOLID principles:
- **S**ingle Responsibility: Each component has one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Components can be substituted with implementations
- **I**nterface Segregation: Specific interfaces for specific needs
- **D**ependency Inversion: Depends on abstractions, not concretions

See ARCHITECTURE.md for detailed explanation.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review ARCHITECTURE.md for system design
3. Check test examples in `src/tests/`

## License

This project is licensed under the MIT License. See LICENSE file for details.
