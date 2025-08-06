"""
Property Search Service - Business Logic Layer
Clean architecture with proper separation of concerns.
"""
import time
from typing import List, Dict
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.repositories.property_repository import PropertyRepository
from app.repositories.property_use_repository import PropertyUseRepository
from app.schemas.search import GeneralSearchInput, PropertyResult, SearchMeta, GeneralSearchResponse


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
    
    def search_properties(self, search_input: GeneralSearchInput) -> GeneralSearchResponse:
        """
        Main search method that orchestrates the entire search process.
        
        Args:
            search_input: Search criteria and filters
            
        Returns:
            GeneralSearchResponse: Formatted search results
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate polygon
            if not self._validate_polygon(search_input.polygon):
                self.logger.warning(f"Invalid polygon provided: {search_input.polygon}")
                return self._create_empty_response(search_input, start_time)
            
            # Step 2: Get properties within polygon
            barmanpre_list = self._get_properties_in_polygon(search_input.polygon)
            if not barmanpre_list:
                self.logger.info("No properties found within the specified polygon")
                return self._create_empty_response(search_input, start_time)
            
            # Step 3: Fetch characteristics data (main filtering table)
            characteristics = self.repository.get_property_characteristics(barmanpre_list)
            if not characteristics:
                self.logger.info("No characteristics data found for properties")
                return self._create_empty_response(search_input, start_time)
            
            # Step 4: Apply business filters to characteristics
            filtered_characteristics = self._apply_business_filters(characteristics, search_input)
            if not filtered_characteristics:
                self.logger.info("No properties match the specified filters")
                return self._create_empty_response(search_input, start_time)
            
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
            meta = self._create_search_meta(search_input, len(property_results), execution_time)
            
            self.logger.info(f"Search completed successfully. Found {len(property_results)} properties in {execution_time:.2f}ms")
            return GeneralSearchResponse(meta=meta, data=property_results)
            
        except Exception as e:
            self.logger.error(f"Error in property search: {e}")
            raise
    
    def _get_properties_in_polygon(self, polygon: str) -> List[str]:
        """Get properties within the specified polygon."""
        return self.repository.get_properties_in_polygon(polygon)
    
    def _apply_business_filters(self, characteristics: List, search_input: GeneralSearchInput) -> List:
        """Apply business logic filters to characteristics."""
        filtered = []
        
        # Get property use codes based on property_type (if not already provided)
        property_use_codes = search_input.property_use_codes
        if not property_use_codes and search_input.property_type:
            property_use_codes = self.property_use_repository.get_property_use_codes_by_type(search_input.property_type)
        
        for char in characteristics:
            # Skip if no characteristics data
            if not char:
                continue
                
            # Area filters (preaconst)
            if search_input.min_area > 0 and (char.preaconst is None or char.preaconst < search_input.min_area):
                continue
            if search_input.max_area > 0 and (char.preaconst is None or char.preaconst > search_input.max_area):
                continue
            
            # Age filters (prevetustzmin/prevetustzmax)
            if search_input.min_age > 0 or search_input.max_age > 0:
                if char.prevetustzmin is not None:
                    current_year = datetime.now().year
                    age = current_year - char.prevetustzmin
                    
                    if search_input.min_age > 0 and age < search_input.min_age:
                        continue
                    if search_input.max_age > 0 and age > search_input.max_age:
                        continue
                else:
                    # If prevetustzmin is None but age filter is applied, filter it out
                    if search_input.min_age > 0 or search_input.max_age > 0:
                        continue
            
            # Stratum filters
            if search_input.min_stratum > 0 and (char.estrato is None or char.estrato < search_input.min_stratum):
                continue
            if search_input.max_stratum > 0 and (char.estrato is None or char.estrato > search_input.max_stratum):
                continue
            
            # Property use codes filter (from property_type or direct input)
            if property_use_codes and char.preusoph not in property_use_codes:
                continue
            
            filtered.append(char)
        
        return filtered
    
    def _validate_polygon(self, polygon: str) -> bool:
        """Validate polygon input."""
        if not polygon or not isinstance(polygon, str):
            return False
        
        # Check for empty or 'none' values
        if polygon.strip() == '' or 'none' in polygon.lower():
            return False
        
        # Basic WKT polygon validation
        if not polygon.upper().startswith('POLYGON'):
            return False
        
        return True
    
    def _transform_to_response_format(self, characteristics: List, property_data: List, 
                                    geometry_data: List[Dict]) -> List[PropertyResult]:
        """Transform database objects to API response format."""
        # Create lookup dictionaries for faster access
        property_lookup = {p.barmanpre: p for p in property_data}
        geometry_lookup = {g["barmanpre"]: g["wkt"] for g in geometry_data}
        
        results = []
        for char in characteristics:
            prop_data = property_lookup.get(char.barmanpre)
            wkt = geometry_lookup.get(char.barmanpre)
            
            result = PropertyResult(
                barmanpre=str(char.barmanpre or ""),
                preaconst=char.preaconst,
                preaterre=char.preaterre,
                prevetustz=char.prevetustzmin,
                precuso=char.preusoph,
                precdestin=None,
                estrato=char.estrato,
                predios=str(char.predios) if char.predios else "0",
                connpisos=str(char.connpisos) if char.connpisos else "0",
                connsotano=str(char.connsotano) if char.connsotano else "0",
                contsemis=str(char.contsemis) if char.contsemis else "0",
                conelevaci=str(char.conelevaci) if char.conelevaci else "0",
                formato_direccion=char.formato_direccion,
                nombre_conjunto=char.nombre_conjunto,
                prenbarrio=char.prenbarrio,
                precbarrio=char.precbarrio,
                locnombre=char.locnombre,
                preusoph=char.preusoph,
                manzcodigo=char.manzcodigo,
                wkt=wkt,
                # Additional fields from property_data if available
                prechip=prop_data.prechip if prop_data else None,
                predirecc=prop_data.predirecc if prop_data else None,
                matriculainmobiliaria=prop_data.matriculainmobiliaria if prop_data else None
            )
            results.append(result)
        
        return results
    
    def _create_search_meta(self, search_input: GeneralSearchInput, total_results: int, 
                          execution_time_ms: float) -> SearchMeta:
        """Create search metadata."""
        import uuid
        
        return SearchMeta(
            total_results=total_results,
            execution_time_ms=execution_time_ms,
            request_id=str(uuid.uuid4()),
            filters_applied={
                "property_type": search_input.property_type,
                "min_area": search_input.min_area,
                "max_area": search_input.max_area,
                "min_age": search_input.min_age,
                "max_age": search_input.max_age,
                "min_stratum": search_input.min_stratum,
                "max_stratum": search_input.max_stratum,
                "property_use_codes": search_input.property_use_codes,
                "polygon": search_input.polygon[:100] + "..." if len(search_input.polygon) > 100 else search_input.polygon
            },
            timestamp=datetime.now()
        )
    
    def _create_empty_response(self, search_input: GeneralSearchInput, start_time: float) -> GeneralSearchResponse:
        """Create empty response when no results found."""
        execution_time = (time.time() - start_time) * 1000
        meta = self._create_search_meta(search_input, 0, execution_time)
        return GeneralSearchResponse(meta=meta, data=[]) 