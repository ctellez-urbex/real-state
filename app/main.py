"""Main FastAPI application with security, logging, and middleware."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import setup_middleware
from app.api.v1.api import api_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Real Estate API", version=settings.VERSION, environment=settings.ENVIRONMENT)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Real Estate API")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Real Estate API with advanced security and performance features",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Setup middleware
setup_middleware(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with application information.
    
    Returns:
        Application information
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "active",
        "timestamp": time.time(),
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/info", tags=["info"])
async def info():
    """Application information endpoint.
    
    Returns:
        Detailed application information
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "features": {
            "api_key_auth": True,
            "rate_limiting": True,
            "security_headers": True,
            "structured_logging": True,
            "performance_monitoring": True,
        },
        "endpoints": {
            "docs": "/docs" if settings.DEBUG else "disabled",
            "redoc": "/redoc" if settings.DEBUG else "disabled",
            "openapi": "/openapi.json" if settings.DEBUG else "disabled",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler.
    
    Args:
        request: Request that caused the exception
        exc: Exception that occurred
        
    Returns:
        Error response
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        "Unhandled exception",
        request_id=request_id,
        path=str(request.url.path),
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc),
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "message": "An unexpected error occurred",
            "timestamp": time.time(),
        },
        headers={"X-Request-ID": request_id},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 