"""
Search schemas for the Real Estate API.

This module contains Pydantic models for search requests and responses,
including validation for search parameters and polygon geometry.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


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
        json_schema_extra={
            "example": "POLYGON((-74.1 4.6, -74.0 4.6, -74.0 4.7, -74.1 4.7, -74.1 4.6))"
        },
    )

    # Property filters
    tipoinmueble: Optional[Union[str, List[str]]] = Field(
        None,
        description="Property type filter (single value or list)",
        json_schema_extra={"example": ["apartamento", "casa"]},
    )

    # Area filters
    min_area: Optional[float] = Field(
        None,
        alias="areamin",
        description="Minimum area in square meters",
        ge=0,
        json_schema_extra={"example": 50.0},
    )
    max_area: Optional[float] = Field(
        None,
        alias="areamax",
        description="Maximum area in square meters",
        ge=0,
        json_schema_extra={"example": 200.0},
    )

    # Age filters
    min_age: Optional[int] = Field(
        None,
        alias="antiguedadmin",
        description="Minimum property age in years",
        ge=0,
        json_schema_extra={"example": 0},
    )
    max_age: Optional[int] = Field(
        None,
        alias="max_age",
        description="Maximum property age in years",
        ge=0,
        json_schema_extra={"example": 10},
    )

    # Stratum filters
    min_stratum: Optional[int] = Field(
        None,
        alias="estratomin",
        description="Minimum stratum (0-6, 0 means no filter)",
        ge=0,
        le=6,
        json_schema_extra={"example": 3},
    )
    max_stratum: Optional[int] = Field(
        None,
        alias="estratomax",
        description="Maximum stratum (0-6, 0 means no filter)",
        ge=0,
        le=6,
        json_schema_extra={"example": 5},
    )

    # Price filters
    min_price: Optional[float] = Field(
        None,
        description="Minimum price in COP",
        ge=0,
        json_schema_extra={"example": 100000000},
    )
    max_price: Optional[float] = Field(
        None,
        description="Maximum price in COP",
        ge=0,
        json_schema_extra={"example": 500000000},
    )

    # Pagination
    limit: Optional[int] = Field(
        100,
        description="Maximum number of results",
        ge=1,
        le=1000,
        json_schema_extra={"example": 50},
    )
    offset: Optional[int] = Field(
        0,
        description="Number of results to skip",
        ge=0,
        json_schema_extra={"example": 0},
    )

    @field_validator("polygon")
    @classmethod
    def validate_polygon(cls, v):
        """Validate polygon WKT format."""
        if v is None:
            return v

        v = v.strip()
        if not v:
            return None

        # Basic WKT polygon validation
        polygon_pattern = r"^POLYGON\s*\(\s*\(\s*([^)]+)\s*\)\s*\)$"
        if not re.match(polygon_pattern, v, re.IGNORECASE):
            raise ValueError(
                "Invalid polygon WKT format. Expected: POLYGON((x1 y1, x2 y2, ...))"
            )

        return v

    @field_validator("max_area")
    @classmethod
    def validate_max_area(cls, v, info):
        """Validate max_area is greater than min_area."""
        if (
            v is not None
            and "min_area" in info.data
            and info.data["min_area"] is not None
            and v != 0  # Allow 0 as "no limit"
            and info.data["min_area"] != 0  # Allow 0 as "no limit"
        ):
            if v <= info.data["min_area"]:
                raise ValueError("max_area must be greater than min_area")
        return v

    @field_validator("max_age")
    @classmethod
    def validate_max_age(cls, v, info):
        """Validate max_age is greater than min_age."""
        if (
            v is not None
            and "min_age" in info.data
            and info.data["min_age"] is not None
            and v != 0  # Allow 0 as "no limit"
            and info.data["min_age"] != 0  # Allow 0 as "no limit"
        ):
            if v <= info.data["min_age"]:
                raise ValueError("max_age must be greater than min_age")
        return v

    @field_validator("max_stratum")
    @classmethod
    def validate_max_stratum(cls, v, info):
        """Validate max_stratum is greater than min_stratum."""
        if (
            v is not None
            and "min_stratum" in info.data
            and info.data["min_stratum"] is not None
            and v != 0  # Allow 0 as "no limit"
            and info.data["min_stratum"] != 0  # Allow 0 as "no limit"
        ):
            if v <= info.data["min_stratum"]:
                raise ValueError("max_stratum must be greater than min_stratum")
        return v

    @field_validator("max_price")
    @classmethod
    def validate_max_price(cls, v, info):
        """Validate max_price is greater than min_price."""
        if (
            v is not None
            and "min_price" in info.data
            and info.data["min_price"] is not None
            and v != 0  # Allow 0 as "no limit"
            and info.data["min_price"] != 0  # Allow 0 as "no limit"
        ):
            if v <= info.data["min_price"]:
                raise ValueError("max_price must be greater than min_price")
        return v


class PropertyResponse(BaseModel):
    """
    Property response model for search results.

    This model represents a single property in the search response,
    including basic information and characteristics.
    """

    id: int = Field(..., description="Property ID")
    barmanpre: str = Field(..., description="Property identifier")
    preaconst: Optional[float] = Field(
        None, description="Construction area in square meters"
    )
    preaterre: Optional[float] = Field(None, description="Land area in square meters")
    prevetustzmin: Optional[int] = Field(
        None, description="Minimum age of the property in years"
    )
    prevetustzmax: Optional[int] = Field(
        None, description="Maximum age of the property in years"
    )
    estrato: Optional[float] = Field(None, description="Socioeconomic stratum (1-6)")
    predios: Optional[int] = Field(None, description="Number of properties in the lot")
    connpisos: Optional[float] = Field(
        None, description="Number of floors in the construction"
    )
    connsotano: Optional[float] = Field(None, description="Number of basement floors")
    contsemis: Optional[float] = Field(
        None, description="Number of semi-basement floors"
    )
    conelevaci: Optional[float] = Field(None, description="Number of elevator floors")
    formato_direccion: Optional[str] = Field(
        None, description="Formatted address of the property"
    )
    nombre_conjunto: Optional[str] = Field(
        None, description="Name of the residential complex"
    )
    prenbarrio: Optional[str] = Field(None, description="Neighborhood name")
    precbarrio: Optional[str] = Field(None, description="Neighborhood code")
    locnombre: Optional[str] = Field(None, description="Locality name")
    preusoph: Optional[str] = Field(None, description="Property use code")
    manzcodigo: Optional[str] = Field(None, description="Block code identifier")
    esquinero: Optional[float] = Field(
        None, description="Corner property indicator (1=corner, 0=not corner)"
    )
    viaprincipal: Optional[float] = Field(
        None, comment="Main road indicator (1=main road, 0=secondary)"
    )
    lista_precuso: Optional[str] = Field(None, description="List of property use codes")
    lista_precdestin: Optional[str] = Field(
        None, description="List of property destination codes"
    )
    wkt: Optional[str] = Field(None, description="Property geometry data")


class ResponseMeta(BaseModel):
    """
    Response metadata model.

    Contains additional information about the request and response.
    """

    timestamp: datetime = Field(..., description="Response timestamp")
    request_id: str = Field(..., description="Unique request identifier")
    filters_applied: Dict[str, Any] = Field(
        ..., description="Filters that were applied to the search"
    )


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
    meta: ResponseMeta = Field(..., description="Response metadata")
