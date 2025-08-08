"""
Property Search Service - Business Logic Layer
Clean architecture with proper separation of concerns.
"""
import time
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.repositories.property_repository import PropertyRepository
from app.repositories.property_use_repository import PropertyUseRepository
from app.schemas.search import (
    PropertyResponse,
    ResponseMeta,
    SearchRequest,
    SearchResponse,
)


class PropertySearchService:
    """
    Clean property search service following proper architecture patterns.

    Responsibilities:
    - Business logic orchestration
    - Data transformation
    - Filter application
    - Response formatting
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = PropertyRepository(db)
        self.property_use_repository = PropertyUseRepository(db)
        self.logger = get_logger(__name__)

    def search_properties(
        self, search_input: SearchRequest, request_id: str, timestamp: datetime
    ) -> SearchResponse:
        """
        Main search method that orchestrates the entire search process.

        Args:
            search_input: Search criteria and filters
            request_id: Unique identifier for this request
            timestamp: Request timestamp

        Returns:
            SearchResponse: Formatted search results with metadata
        """
        start_time = time.time()

        try:
            # Step 1: Validate polygon
            if search_input.polygon and not self._validate_polygon(
                search_input.polygon
            ):
                self.logger.warning(f"Invalid polygon provided: {search_input.polygon}")
                return self._create_empty_response(search_input, request_id, timestamp)

            # Step 2: Get properties within polygon (if provided)
            barmanpre_list = []
            if search_input.polygon:
                barmanpre_list = self._get_properties_in_polygon(search_input.polygon)
                if not barmanpre_list:
                    self.logger.info("No properties found within the specified polygon")
                    return self._create_empty_response(
                        search_input, request_id, timestamp
                    )

            # Step 3: Fetch characteristics data (main filtering table)
            characteristics = (
                self.repository.get_property_characteristics(barmanpre_list)
                if barmanpre_list
                else []
            )

            # Step 4: Apply business filters to characteristics
            filtered_characteristics = self._apply_business_filters(
                characteristics, search_input
            )
            if not filtered_characteristics:
                self.logger.info("No properties match the specified filters")
                return self._create_empty_response(search_input, request_id, timestamp)

            # Step 5: Get additional data only for filtered properties
            final_barmanpre = [c.barmanpre for c in filtered_characteristics]
            property_data = self.repository.get_property_data(final_barmanpre)
            geometry_data = self.repository.get_property_geometry(final_barmanpre)

            # Step 6: Transform to response format
            property_results = self._transform_to_response_format(
                filtered_characteristics, property_data, geometry_data
            )

            # Step 7: Create response
            execution_time = (time.time() - start_time) * 1000

            self.logger.info(
                f"Search completed successfully. Found {len(property_results)} properties in {execution_time:.2f}ms"
            )
            return SearchResponse(
                success=True,
                message=f"Found {len(property_results)} properties",
                meta=self._create_response_meta(search_input, request_id, timestamp),
                data=property_results,
                total=len(property_results),
                limit=search_input.limit,
                offset=search_input.offset,
            )

        except Exception as e:
            self.logger.error(f"Error in property search: {e}")
            raise

    def _get_properties_in_polygon(self, polygon: str) -> List[str]:
        """Get properties within the specified polygon."""
        return self.repository.get_properties_in_polygon(polygon)

    def _apply_business_filters(
        self, characteristics: List, search_input: SearchRequest
    ) -> List:
        """Apply business logic filters to characteristics."""
        filtered = []

        for char in characteristics:
            # Area filters
            if (
                search_input.min_area
                and char.preaconst
                and char.preaconst < search_input.min_area
            ):
                continue
            if (
                search_input.max_area
                and char.preaconst
                and char.preaconst > search_input.max_area
            ):
                continue

            # Age filters - using prevetustzmin and prevetustzmax instead of prevetustz
            if (
                search_input.min_age
                and char.prevetustzmin
                and char.prevetustzmin < search_input.min_age
            ):
                continue
            if (
                search_input.max_age
                and char.prevetustzmax
                and char.prevetustzmax > search_input.max_age
            ):
                continue

            # Stratum filters
            if (
                search_input.min_stratum
                and char.estrato
                and char.estrato < search_input.min_stratum
            ):
                continue
            if (
                search_input.max_stratum
                and char.estrato
                and char.estrato > search_input.max_stratum
            ):
                continue

            filtered.append(char)

        return filtered

    def _validate_polygon(self, polygon: str) -> bool:
        """Validate polygon WKT format."""
        if not polygon or not isinstance(polygon, str):
            return False

        # Basic WKT polygon validation
        if not polygon.upper().startswith("POLYGON"):
            return False

        return True

    def _transform_to_response_format(
        self, characteristics: List, property_data: List, geometry_data: List[Dict]
    ) -> List[PropertyResponse]:
        """Transform database results to response format."""
        results = []

        # Create lookup dictionaries for faster access
        property_lookup = (
            {p.barmanpre: p for p in property_data} if property_data else {}
        )
        geometry_lookup = (
            {g.get("barmanpre"): g for g in geometry_data} if geometry_data else {}
        )

        for char in characteristics:
            property_info = property_lookup.get(char.barmanpre, {})
            geometry_info = geometry_lookup.get(char.barmanpre, {})

            # Create characteristics dict with only existing fields
            char_dict = {
                "id": char.id,
                "barmanpre": char.barmanpre,
                "preaconst": char.preaconst,
                "preaterre": char.preaterre,
                "prevetustzmin": char.prevetustzmin,
                "prevetustzmax": char.prevetustzmax,
                "estrato": char.estrato,
                "predios": char.predios,
                "connpisos": char.connpisos,
                "connsotano": char.connsotano,
                "contsemis": char.contsemis,
                "conelevaci": char.conelevaci,
                "formato_direccion": char.formato_direccion,
                "nombre_conjunto": char.nombre_conjunto,
                "prenbarrio": char.prenbarrio,
                "precbarrio": char.precbarrio,
                "locnombre": char.locnombre,
                "preusoph": char.preusoph,
                "manzcodigo": char.manzcodigo,
                "esquinero": char.esquinero,
                "viaprincipal": char.viaprincipal,
                "lista_precuso": char.lista_precuso,
                "lista_precdestin": char.lista_precdestin,
            }

            # Create property response
            result = PropertyResponse(
                **char_dict,
                wkt=geometry_info.get("wkt"),
            )

            results.append(result)

        return results

    def _create_response_meta(
        self, search_input: SearchRequest, request_id: str, timestamp: datetime
    ) -> ResponseMeta:
        """Create response metadata with applied filters."""
        # Extract ALL applied filters from the original request (non-None and non-zero values)
        filters_applied = {}

        # Get all fields from the search_input model using aliases (original field names)
        for field_name, field_value in search_input.model_dump(by_alias=True).items():
            # Include filter if it has a meaningful value
            if field_value is not None:
                # Special handling for different field types
                if isinstance(field_value, str):
                    if field_value.strip():  # Non-empty string
                        if field_name == "polygon":
                            # Truncate long polygon strings
                            filters_applied[field_name] = (
                                field_value[:100] + "..."
                                if len(field_value) > 100
                                else field_value
                            )
                        else:
                            filters_applied[field_name] = field_value
                elif isinstance(field_value, list):
                    if field_value:  # Non-empty list
                        filters_applied[field_name] = field_value
                elif isinstance(field_value, (int, float)):
                    # Include non-zero numbers or if they are meaningful defaults
                    if field_value != 0 or field_name in ["limit", "offset"]:
                        # Only include limit/offset if different from defaults
                        if field_name == "limit" and field_value == 100:
                            continue  # Skip default limit
                        elif field_name == "offset" and field_value == 0:
                            continue  # Skip default offset
                        else:
                            filters_applied[field_name] = field_value
                else:
                    # Include any other non-None values
                    filters_applied[field_name] = field_value

        return ResponseMeta(
            timestamp=timestamp, request_id=request_id, filters_applied=filters_applied
        )

    def _create_empty_response(
        self, search_input: SearchRequest, request_id: str, timestamp: datetime
    ) -> SearchResponse:
        """Create empty response when no results found."""
        return SearchResponse(
            success=True,
            message="No properties found matching the criteria",
            data=[],
            total=0,
            limit=search_input.limit,
            offset=search_input.offset,
            meta=self._create_response_meta(search_input, request_id, timestamp),
        )
