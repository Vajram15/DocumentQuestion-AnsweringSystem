#!/usr/bin/env python
"""Test the API endpoints"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_upload():
    """Test document upload"""
    print("\n=== Testing Document Upload ===")
    url = f"{BASE_URL}/documents/upload"
    data = {
        "name": "Paris Facts",
        "content": """Paris is the capital of France and is located in the northern part of the country.
The Eiffel Tower is an iconic iron lattice tower located in Paris.
Paris is known worldwide as the City of Light due to its architecture and culture.
The population of Paris is approximately 2 million people in the city proper.
The River Seine flows through Paris, dividing the city into left and right banks."""
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        return result.get("document_id")
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_ask_question(document_id):
    """Test asking a question"""
    print("\n=== Testing Question Answering ===")
    url = f"{BASE_URL}/qa/ask"
    
    questions = [
        "What is Paris?",
        "Where is the Eiffel Tower?",
        "What is the population of Paris?",
        "What does Paris flow through?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        data = {
            "question": question,
            "document_id": document_id,
            "k": 3
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Answer: {result.get('answer')[:200]}...")
            print(f"Confidence: {result.get('confidence')}")
            print(f"Sources: {len(result.get('sources', []))} found")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    time.sleep(1)  # Give server time to start if needed
    
    doc_id = test_upload()
    if doc_id:
        test_ask_question(doc_id)
    else:
        print("Failed to upload document")
