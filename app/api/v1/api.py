"""Main API router with all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import search

api_router = APIRouter()

# Include search endpoints
api_router.include_router(search.router, prefix="/search", tags=["search"])

# Root endpoint with documentation
@api_router.get("/")
async def root():
    """
    Real Estate API - Clean Architecture
    
    Available endpoints:
    - /api/v1/search/general (Property search)
    - /api/v1/search/health (Health check)
    - /api/v1/search/metrics (Performance metrics)
    
    Architecture:
    - Clean layered architecture
    - Proper separation of concerns
    - Repository pattern for data access
    - Service layer for business logic
    - Dependency injection
    """
    return {
        "message": "Real Estate API",
        "version": "1.0.0",
        "architecture": "clean-layered",
        "endpoints": {
            "search": "/api/v1/search/general",
            "health": "/api/v1/search/health",
            "metrics": "/api/v1/search/metrics",
            "docs": "/docs"
        },
        "description": "Clean architecture with proper separation of concerns"
    } 