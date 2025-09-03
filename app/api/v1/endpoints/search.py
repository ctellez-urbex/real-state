"""
Search Endpoints - Clean Architecture
Proper separation of concerns with clean dependency injection.
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.search import SearchRequest, SearchResponse
from app.services.property_search import PropertySearch

router = APIRouter()
logger = get_logger(__name__)


def get_search_service(db: Session = Depends(get_db)) -> PropertySearch:
    """Dependency injection for search service."""
    return PropertySearch(db)


@router.post("/general", response_model=SearchResponse)
async def general_search(
    search_input: SearchRequest,
    background_tasks: BackgroundTasks,
    search_service: PropertySearch = Depends(get_search_service),
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
        # Generate request metadata
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        logger.info(
            f"[{request_id}] Received search request with polygon: {search_input.polygon[:50] if search_input.polygon else 'None'}..."
        )

        # Add background task for metrics collection
        background_tasks.add_task(_collect_search_metrics, search_input, request_id)

        # Execute search using clean service
        result = search_service.search_properties(search_input, request_id, timestamp)

        logger.info(
            f"[{request_id}] Search completed. Found {len(result.data)} properties"
        )
        return result

    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred during the search"
        )


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
            "architecture": "clean-layered",
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
            "success_rate": 100.0,
        },
        "timestamp": "2025-08-05T00:00:00.000000",
    }


async def _collect_search_metrics(search_input: SearchRequest, request_id: str):
    """Background task to collect search metrics."""
    # TODO: Implement metrics collection
    logger.info(
        f"[{request_id}] Collecting metrics for search: {search_input.tipoinmueble}"
    )
