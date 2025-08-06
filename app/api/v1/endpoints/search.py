"""
Search Endpoints - Clean Architecture
Proper separation of concerns with clean dependency injection.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import get_logger
from app.services.property_search_service import PropertySearchService
from app.schemas.search import GeneralSearchInput, GeneralSearchResponse

router = APIRouter()
logger = get_logger(__name__)


def get_search_service(db: Session = Depends(get_db)) -> PropertySearchService:
    """Dependency injection for search service."""
    return PropertySearchService(db)


@router.post("/general", response_model=GeneralSearchResponse)
async def general_search(
    search_input: GeneralSearchInput,
    background_tasks: BackgroundTasks,
    search_service: PropertySearchService = Depends(get_search_service)
):
    """
    Property search endpoint with clean architecture.
    
    Features:
    - Proper separation of concerns
    - Clean dependency injection
    - Business logic in service layer
    - Data access in repository layer
    - Background task support for metrics
    """
    try:
        logger.info(f"Received search request with polygon: {search_input.polygon[:50]}...")
        
        # Add background task for metrics collection
        background_tasks.add_task(_collect_search_metrics, search_input)
        
        # Execute search using clean service
        result = search_service.search_properties(search_input)
        
        logger.info(f"Search completed. Found {len(result.data)} properties")
        return result
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the search")


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for the service."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "property-search",
            "timestamp": "2025-08-05T00:00:00.000000",
            "version": "1.0.0",
            "architecture": "clean-layered"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/metrics")
async def get_metrics():
    """Get service metrics."""
    return {
        "service": "property-search",
        "metrics": {
            "total_searches": 0,  # TODO: Implement metrics collection
            "average_response_time": 0,
            "success_rate": 100.0
        },
        "timestamp": "2025-08-05T00:00:00.000000"
    }


async def _collect_search_metrics(search_input: GeneralSearchInput):
    """Background task to collect search metrics."""
    # TODO: Implement metrics collection
    logger.info(f"Collecting metrics for search: {search_input.property_type}") 