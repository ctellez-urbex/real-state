"""
Search schemas for the Real Estate API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class GeneralSearchInput(BaseModel):
    """Input schema for general property search."""
    
    # Property type filter
    property_type: List[str] = Field(
        default=["All"], 
        description="List of property types to filter by"
    )
    
    # Area filters (in square meters)
    min_area: float = Field(
        default=0.0, 
        ge=0.0, 
        description="Minimum built area in square meters"
    )
    max_area: float = Field(
        default=0.0, 
        ge=0.0, 
        description="Maximum built area in square meters"
    )
    
    # Age filters (in years)
    min_age: int = Field(
        default=0, 
        ge=0, 
        description="Minimum property age in years"
    )
    max_age: int = Field(
        default=0, 
        ge=0, 
        description="Maximum property age in years"
    )
    
    # Socioeconomic stratum filters
    min_stratum: int = Field(
        default=0, 
        ge=0, 
        le=6, 
        description="Minimum socioeconomic stratum (0-6)"
    )
    max_stratum: int = Field(
        default=0, 
        ge=0, 
        le=6, 
        description="Maximum socioeconomic stratum (0-6)"
    )
    
    # Property use codes
    property_use_codes: List[str] = Field(
        default=[], 
        description="List of property use codes to filter by"
    )
    
    # Geographic polygon (WKT format)
    polygon: str = Field(
        ..., 
        description="WKT polygon for geographic search (e.g., 'POLYGON ((-74.052315 4.690699, ...))')"
    )
    
    @validator('polygon')
    def validate_polygon(cls, v):
        """Validate that polygon is a valid WKT format."""
        if not v or not isinstance(v, str):
            raise ValueError('Polygon is required and must be a string')
        
        # Basic WKT polygon validation
        if not v.upper().startswith('POLYGON'):
            raise ValueError('Polygon must be in WKT POLYGON format')
        
        return v
    
    @validator('max_area')
    def validate_area_range(cls, v, values):
        """Validate that max_area is greater than min_area when both are specified."""
        min_area = values.get('min_area', 0)
        if v > 0 and min_area > 0 and v < min_area:
            raise ValueError('max_area must be greater than min_area')
        return v
    
    @validator('max_age')
    def validate_age_range(cls, v, values):
        """Validate that max_age is greater than min_age when both are specified."""
        min_age = values.get('min_age', 0)
        if v > 0 and min_age > 0 and v < min_age:
            raise ValueError('max_age must be greater than min_age')
        return v
    
    @validator('max_stratum')
    def validate_stratum_range(cls, v, values):
        """Validate that max_stratum is greater than min_stratum when both are specified."""
        min_stratum = values.get('min_stratum', 0)
        if v > 0 and min_stratum > 0 and v < min_stratum:
            raise ValueError('max_stratum must be greater than min_stratum')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "property_type": ["Residential", "Commercial"],
                "min_area": 50.0,
                "max_area": 200.0,
                "min_age": 0,
                "max_age": 20,
                "min_stratum": 3,
                "max_stratum": 5,
                "property_use_codes": ["001", "002"],
                "polygon": "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))"
            }
        }


class PropertyResult(BaseModel):
    """Schema for individual property search result."""
    
    barmanpre: str = Field(..., description="Barmanpre property identifier")
    preaconst: Optional[float] = Field(None, description="Built area in square meters")
    preaterre: Optional[float] = Field(None, description="Land area in square meters")
    prevetustz: Optional[int] = Field(None, description="Property age in years")
    precuso: Optional[str] = Field(None, description="Property use code")
    precdestin: Optional[str] = Field(None, description="Property destination code")
    estrato: Optional[int] = Field(None, description="Socioeconomic stratum")
    predios: Optional[str] = Field(None, description="Property information")
    connpisos: Optional[str] = Field(None, description="Floor information")
    connsotano: Optional[str] = Field(None, description="Basement information")
    contsemis: Optional[str] = Field(None, description="Semi-basement information")
    conelevaci: Optional[str] = Field(None, description="Elevation information")
    formato_direccion: Optional[str] = Field(None, description="Formatted address")
    nombre_conjunto: Optional[str] = Field(None, description="Building complex name")
    prenbarrio: Optional[str] = Field(None, description="Neighborhood name")
    precbarrio: Optional[str] = Field(None, description="Neighborhood code")
    locnombre: Optional[str] = Field(None, description="District name")
    preusoph: Optional[str] = Field(None, description="Property use")
    manzcodigo: Optional[str] = Field(None, description="Block code")
    wkt: Optional[str] = Field(None, description="WKT geometry representation")
    prechip: Optional[str] = Field(None, description="Property chip code")
    predirecc: Optional[str] = Field(None, description="Property address")
    matriculainmobiliaria: Optional[str] = Field(None, description="Property registration number")
    
    class Config:
        from_attributes = True


class SearchMeta(BaseModel):
    """Metadata for search results."""
    
    timestamp: datetime = Field(..., description="Search execution timestamp")
    request_id: str = Field(..., description="Unique request identifier")
    total_results: int = Field(..., description="Total number of results found")
    filters_applied: dict = Field(..., description="Filters applied to the search")
    execution_time_ms: float = Field(..., description="Search execution time in milliseconds")
    
    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00.000Z",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_results": 150,
                "filters_applied": {
                    "property_type": ["Residential"],
                    "min_area": 50.0,
                    "max_area": 200.0
                },
                "execution_time_ms": 245.67
            }
        }


class GeneralSearchResponse(BaseModel):
    """Response schema for general property search."""
    
    meta: SearchMeta = Field(..., description="Search metadata")
    data: List[PropertyResult] = Field(..., description="List of property results")
    
    class Config:
        schema_extra = {
            "example": {
                "meta": {
                    "timestamp": "2024-01-15T10:30:00.000Z",
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "total_results": 150,
                    "filters_applied": {
                        "property_type": ["Residential"],
                        "min_area": 50.0,
                        "max_area": 200.0
                    },
                    "execution_time_ms": 245.67
                },
                "data": [
                    {
                        "barmanpre": "1100100000000000001",
                        "preaconst": 120.5,
                        "preaterre": 150.0,
                        "prevetustz": 15,
                        "estrato": 4,
                        "prenbarrio": "Chapinero",
                        "wkt": "POINT (-74.052315 4.690699)"
                    }
                ]
            }
        } 