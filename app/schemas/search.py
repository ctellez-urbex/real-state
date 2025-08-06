"""
Search schemas for the Real Estate API.

This module contains Pydantic models for search requests and responses,
including validation for search parameters and polygon geometry.
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
import re


class SearchRequest(BaseModel):
    """
    Search request model for property search.
    
    This model validates and processes search parameters including
    polygon geometry, property filters, and pagination options.
    """
    
    # Geometry search
    polygon: Optional[str] = Field(
        None,
        description="WKT polygon for spatial search",
        json_schema_extra={"example": "POLYGON((-74.1 4.6, -74.0 4.6, -74.0 4.7, -74.1 4.7, -74.1 4.6))"}
    )
    
    # Property filters
    tipoinmueble: Optional[Union[str, List[str]]] = Field(
        None,
        description="Property type filter (single value or list)",
        json_schema_extra={"example": ["apartamento", "casa"]}
    )
    
    # Area filters
    min_area: Optional[float] = Field(
        None,
        description="Minimum area in square meters",
        ge=0,
        json_schema_extra={"example": 50.0}
    )
    max_area: Optional[float] = Field(
        None,
        description="Maximum area in square meters",
        ge=0,
        json_schema_extra={"example": 200.0}
    )
    
    # Age filters
    min_age: Optional[int] = Field(
        None,
        description="Minimum property age in years",
        ge=0,
        json_schema_extra={"example": 0}
    )
    max_age: Optional[int] = Field(
        None,
        description="Maximum property age in years",
        ge=0,
        json_schema_extra={"example": 10}
    )
    
    # Stratum filters
    min_stratum: Optional[int] = Field(
        None,
        description="Minimum stratum (1-6)",
        ge=1,
        le=6,
        json_schema_extra={"example": 3}
    )
    max_stratum: Optional[int] = Field(
        None,
        description="Maximum stratum (1-6)",
        ge=1,
        le=6,
        json_schema_extra={"example": 5}
    )
    
    # Price filters
    min_price: Optional[float] = Field(
        None,
        description="Minimum price in COP",
        ge=0,
        json_schema_extra={"example": 100000000}
    )
    max_price: Optional[float] = Field(
        None,
        description="Maximum price in COP",
        ge=0,
        json_schema_extra={"example": 500000000}
    )
    
    # Pagination
    limit: Optional[int] = Field(
        100,
        description="Maximum number of results",
        ge=1,
        le=1000,
        json_schema_extra={"example": 50}
    )
    offset: Optional[int] = Field(
        0,
        description="Number of results to skip",
        ge=0,
        json_schema_extra={"example": 0}
    )

    @field_validator('polygon')
    @classmethod
    def validate_polygon(cls, v):
        """Validate polygon WKT format."""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
            
        # Basic WKT polygon validation
        polygon_pattern = r'^POLYGON\s*\(\s*\(\s*([^)]+)\s*\)\s*\)$'
        if not re.match(polygon_pattern, v, re.IGNORECASE):
            raise ValueError('Invalid polygon WKT format. Expected: POLYGON((x1 y1, x2 y2, ...))')
        
        return v

    @field_validator('max_area')
    @classmethod
    def validate_max_area(cls, v, info):
        """Validate max_area is greater than min_area."""
        if v is not None and 'min_area' in info.data and info.data['min_area'] is not None:
            if v <= info.data['min_area']:
                raise ValueError('max_area must be greater than min_area')
        return v

    @field_validator('max_age')
    @classmethod
    def validate_max_age(cls, v, info):
        """Validate max_age is greater than min_age."""
        if v is not None and 'min_age' in info.data and info.data['min_age'] is not None:
            if v <= info.data['min_age']:
                raise ValueError('max_age must be greater than min_age')
        return v

    @field_validator('max_stratum')
    @classmethod
    def validate_max_stratum(cls, v, info):
        """Validate max_stratum is greater than min_stratum."""
        if v is not None and 'min_stratum' in info.data and info.data['min_stratum'] is not None:
            if v <= info.data['min_stratum']:
                raise ValueError('max_stratum must be greater than min_stratum')
        return v

    @field_validator('max_price')
    @classmethod
    def validate_max_price(cls, v, info):
        """Validate max_price is greater than min_price."""
        if v is not None and 'min_price' in info.data and info.data['min_price'] is not None:
            if v <= info.data['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v


class PropertyResponse(BaseModel):
    """
    Property response model for search results.
    
    This model represents a single property in the search response,
    including basic information and characteristics.
    """
    
    id: int = Field(..., description="Property ID")
    title: str = Field(..., description="Property title")
    description: Optional[str] = Field(None, description="Property description")
    price: Optional[float] = Field(None, description="Property price in COP")
    property_type: Optional[str] = Field(None, description="Property type")
    area: Optional[float] = Field(None, description="Property area in square meters")
    address: Optional[str] = Field(None, description="Property address")
    city: Optional[str] = Field(None, description="Property city")
    state: Optional[str] = Field(None, description="Property state")
    zip_code: Optional[str] = Field(None, description="Property zip code")
    is_available: bool = Field(True, description="Property availability status")
    characteristics: Optional[dict] = Field(None, description="Property characteristics")
    geometry: Optional[dict] = Field(None, description="Property geometry data")


class SearchResponse(BaseModel):
    """
    Search response model.
    
    This model represents the complete search response including
    results, pagination information, and metadata.
    """
    
    success: bool = Field(..., description="Search success status")
    message: str = Field(..., description="Response message")
    data: List[PropertyResponse] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    limit: int = Field(..., description="Results limit used")
    offset: int = Field(..., description="Results offset used")
    request_id: Optional[str] = Field(None, description="Unique request identifier") 