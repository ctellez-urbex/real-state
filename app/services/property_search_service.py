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
from app.schemas.search import SearchRequest, PropertyResponse, SearchResponse


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
    
    def search_properties(self, search_input: SearchRequest) -> SearchResponse:
        """
        Main search method that orchestrates the entire search process.
        
        Args:
            search_input: Search criteria and filters
            
        Returns:
            SearchResponse: Formatted search results
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate polygon
            if search_input.polygon and not self._validate_polygon(search_input.polygon):
                self.logger.warning(f"Invalid polygon provided: {search_input.polygon}")
                return self._create_empty_response(search_input, start_time)
            
            # Step 2: Get properties within polygon (if provided)
            barmanpre_list = []
            if search_input.polygon:
                barmanpre_list = self._get_properties_in_polygon(search_input.polygon)
                if not barmanpre_list:
                    self.logger.info("No properties found within the specified polygon")
                    return self._create_empty_response(search_input, start_time)
            
            # Step 3: Fetch characteristics data (main filtering table)
            characteristics = self.repository.get_property_characteristics(barmanpre_list) if barmanpre_list else []
            
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
            
            self.logger.info(f"Search completed successfully. Found {len(property_results)} properties in {execution_time:.2f}ms")
            return SearchResponse(
                success=True,
                message=f"Found {len(property_results)} properties",
                data=property_results,
                total=len(property_results),
                limit=search_input.limit,
                offset=search_input.offset,
                request_id=f"req_{int(time.time())}"
            )
            
        except Exception as e:
            self.logger.error(f"Error in property search: {e}")
            raise
    
    def _get_properties_in_polygon(self, polygon: str) -> List[str]:
        """Get properties within the specified polygon."""
        return self.repository.get_properties_in_polygon(polygon)
    
    def _apply_business_filters(self, characteristics: List, search_input: SearchRequest) -> List:
        """Apply business logic filters to characteristics."""
        filtered = []
        
        # Get property use codes based on tipoinmueble
        property_use_codes = []
        if search_input.tipoinmueble:
            if isinstance(search_input.tipoinmueble, list):
                property_use_codes = self.property_use_repository.get_property_use_codes_by_type(search_input.tipoinmueble)
            else:
                property_use_codes = self.property_use_repository.get_property_use_codes_by_type([search_input.tipoinmueble])
        
        for char in characteristics:
            # Property type filter
            if property_use_codes and char.precuso not in property_use_codes:
                continue
            
            # Area filters
            if search_input.min_area and char.preaconst and char.preaconst < search_input.min_area:
                continue
            if search_input.max_area and char.preaconst and char.preaconst > search_input.max_area:
                continue
            
            # Age filters
            if search_input.min_age and char.prevetustz and char.prevetustz < search_input.min_age:
                continue
            if search_input.max_age and char.prevetustz and char.prevetustz > search_input.max_age:
                continue
            
            # Stratum filters
            if search_input.min_stratum and char.estrato and char.estrato < search_input.min_stratum:
                continue
            if search_input.max_stratum and char.estrato and char.estrato > search_input.max_stratum:
                continue
            
            filtered.append(char)
        
        return filtered
    
    def _validate_polygon(self, polygon: str) -> bool:
        """Validate polygon WKT format."""
        if not polygon or not isinstance(polygon, str):
            return False
        
        # Basic WKT polygon validation
        if not polygon.upper().startswith('POLYGON'):
            return False
        
        return True
    
    def _transform_to_response_format(self, characteristics: List, property_data: List, 
                                    geometry_data: List[Dict]) -> List[PropertyResponse]:
        """Transform database results to response format."""
        results = []
        
        # Create lookup dictionaries for faster access
        property_lookup = {p.barmanpre: p for p in property_data} if property_data else {}
        geometry_lookup = {g.get('barmanpre'): g for g in geometry_data} if geometry_data else {}
        
        for char in characteristics:
            property_info = property_lookup.get(char.barmanpre, {})
            geometry_info = geometry_lookup.get(char.barmanpre, {})
            
            # Create characteristics dict
            char_dict = {
                'barmanpre': char.barmanpre,
                'preaconst': char.preaconst,
                'preaterre': char.preaterre,
                'prevetustz': char.prevetustz,
                'precuso': char.precuso,
                'precdestin': char.precdestin,
                'estrato': char.estrato,
                'predios': char.predios,
                'connpisos': char.connpisos,
                'connsotano': char.connsotano,
                'contsemis': char.contsemis,
                'conelevaci': char.conelevaci,
                'formato_direccion': char.formato_direccion,
                'nombre_conjunto': char.nombre_conjunto,
                'prenbarrio': char.prenbarrio,
                'precbarrio': char.precbarrio,
                'locnombre': char.locnombre,
                'preusoph': char.preusoph,
                'manzcodigo': char.manzcodigo,
                'prechip': char.prechip,
                'predirecc': char.predirecc,
                'matriculainmobiliaria': char.matriculainmobiliaria
            }
            
            # Create property response
            result = PropertyResponse(
                id=int(char.barmanpre) if char.barmanpre.isdigit() else hash(char.barmanpre) % 1000000,
                title=f"Property {char.barmanpre}",
                description=f"Property in {char.prenbarrio or 'Unknown'} neighborhood",
                price=None,  # Price not available in current data
                property_type=char.preusoph,
                area=char.preaconst,
                address=char.predirecc or char.formato_direccion,
                city="Bogotá",
                state="Cundinamarca",
                zip_code=None,
                is_available=True,
                characteristics=char_dict,
                geometry=geometry_info
            )
            
            results.append(result)
        
        return results
    
    def _create_empty_response(self, search_input: SearchRequest, start_time: float) -> SearchResponse:
        """Create empty response when no results found."""
        return SearchResponse(
            success=True,
            message="No properties found matching the criteria",
            data=[],
            total=0,
            limit=search_input.limit,
            offset=search_input.offset,
            request_id=f"req_{int(time.time())}"
        ) 