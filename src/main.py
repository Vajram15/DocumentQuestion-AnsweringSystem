"""
FastAPI application entry point
Main application factory and configuration
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.config import get_settings
from src.models import HealthResponse
from src.api.routes import documents, questions
from src.utils.logger import logger
from src.api.dependencies import DIContainer


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI application
    """
    settings = get_settings()
    
    # Initialize application
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        description="A document question-answering system using LangChain and FastAPI"
    )
    
    # Initialize Dependency Injection Container
    try:
        DIContainer.get_instance()
        logger.info("DI Container initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize DI Container: {str(e)}")
        raise
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get(
        "/health",
        response_model=HealthResponse,
        status_code=status.HTTP_200_OK,
        tags=["health"]
    )
    async def health_check() -> HealthResponse:
        """
        Health check endpoint
        
        Returns:
            Service health status
        """
        return HealthResponse(status="ok", version=settings.APP_VERSION)
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        """Root endpoint with API information"""
        return {
            "message": "Document Question-Answering System",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    # Include routers
    app.include_router(documents.router)
    app.include_router(questions.router)
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error", "details": str(exc)}
        )
    
    logger.info(f"FastAPI application initialized: {settings.APP_NAME} v{settings.APP_VERSION}")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    )
