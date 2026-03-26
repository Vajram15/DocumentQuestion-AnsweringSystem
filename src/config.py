"""
Configuration management using Pydantic Settings
Centralized configuration following SOLID principles
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    APP_NAME: str = "Document Question-Answering System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Document Processing
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    
    # Vector Store
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    
    # Storage
    DOCUMENTS_DIR: str = "documents"
    VECTOR_STORE_DIR: str = "vector_store"
    
    # API Settings
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Dependency injection for settings
    Singleton pattern with caching
    """
    return Settings()
