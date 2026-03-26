"""
Logger configuration
Centralized logging setup following SOLID principles
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger instance
    
    Single Responsibility: Only handles logging configuration
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logger("doc_qa_system")
