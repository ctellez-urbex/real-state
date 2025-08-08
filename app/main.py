"""Main FastAPI application with security, logging, and middleware."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.api.v1.endpoints import search
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager."""
    # Startup
    print("Starting Urbex API...")
    yield
    # Shutdown
    print("Shutting down Urbex API...")


# Create FastAPI application
def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Real Estate API with advanced security and performance features",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )

    # Add no-cache middleware
    @app.middleware("http")
    async def add_no_cache_headers(request: Request, call_next):
        """Add headers to prevent caching."""
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Global exception handler."""
        print(f"❌ Global exception handler caught: {exc}")
        print(f"❌ Exception type: {type(exc).__name__}")
        import traceback

        print(f"❌ Traceback: {traceback.format_exc()}")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "detail": str(exc)
                if settings.debug
                else "An unexpected error occurred",
            },
        )

    # Include API routes
    app.include_router(search.router, prefix="/api/v1/search")

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
        }

    # Root endpoint
    @app.get("/")
    async def root() -> dict[str, Any]:
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else None,
        }

    return app


# Create the application instance
app = create_app()

# Create Mangum handler for AWS Lambda
handler = Mangum(app, lifespan="off")
