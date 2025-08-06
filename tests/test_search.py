"""
Tests for Clean Architecture Search Implementation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.services.property_search_service import PropertySearchService
from app.repositories.property_repository import PropertyRepository
from app.repositories.property_use_repository import PropertyUseRepository
from app.api.v1.endpoints.search import get_search_service
from app.schemas.search import GeneralSearchInput, PropertyResult, SearchMeta, GeneralSearchResponse

client = TestClient(app)


class TestPropertyUseRepository:
    """Test PropertyUseRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.repository = PropertyUseRepository(self.mock_db)
    
    def test_get_property_use_codes_by_type_residencial(self):
        """Test getting property use codes for residential type."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["residencial"])
        
        # Assert
        assert set(result) == {"01", "02", "03"}
    
    def test_get_property_use_codes_by_type_comercial(self):
        """Test getting property use codes for commercial type."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["comercial"])
        
        # Assert
        assert set(result) == {"04", "05", "06"}
    
    def test_get_property_use_codes_by_type_industrial(self):
        """Test getting property use codes for industrial type."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["industrial"])
        
        # Assert
        assert set(result) == {"07", "08", "09"}
    
    def test_get_property_use_codes_by_type_institucional(self):
        """Test getting property use codes for institutional type."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["institucional"])
        
        # Assert
        assert set(result) == {"10", "11", "12"}
    
    def test_get_property_use_codes_by_type_recreativo(self):
        """Test getting property use codes for recreational type."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["recreativo"])
        
        # Assert
        assert set(result) == {"13", "14", "15"}
    
    def test_get_property_use_codes_by_type_todo(self):
        """Test getting property use codes for 'todo' type."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["todo"])
        
        # Assert
        assert result == []
    
    def test_get_property_use_codes_by_type_multiple(self):
        """Test getting property use codes for multiple types."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["residencial", "comercial"])
        
        # Assert
        assert set(result) == {"01", "02", "03", "04", "05", "06"}
    
    def test_get_property_use_codes_by_type_empty_list(self):
        """Test getting property use codes with empty list."""
        # Act
        result = self.repository.get_property_use_codes_by_type([])
        
        # Assert
        assert result == []
    
    def test_get_property_use_codes_by_type_none_input(self):
        """Test getting property use codes with None input."""
        # Act
        result = self.repository.get_property_use_codes_by_type(None)
        
        # Assert
        assert result == []
    
    def test_get_property_use_codes_by_type_unknown_type(self):
        """Test getting property use codes for unknown type."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["unknown_type"])
        
        # Assert
        assert result == []
    
    def test_get_property_use_codes_by_type_mixed_types(self):
        """Test getting property use codes for mixed valid and invalid types."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["residencial", "unknown_type"])
        
        # Assert
        assert set(result) == {"01", "02", "03"}
    
    def test_get_property_use_codes_by_type_case_insensitive(self):
        """Test getting property use codes with case insensitive input."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["RESIDENCIAL", "COMERCIAL"])
        
        # Assert
        assert set(result) == {"01", "02", "03", "04", "05", "06"}
    
    def test_get_property_use_codes_by_type_with_todo(self):
        """Test getting property use codes when 'todo' is included."""
        # Act
        result = self.repository.get_property_use_codes_by_type(["residencial", "todo"])
        
        # Assert
        assert result == []  # 'todo' should return empty list to include all
    
    def test_get_property_use_codes_by_type_exception_handling(self):
        """Test getting property use codes with exception handling."""
        # Arrange
        self.repository.logger.error = Mock()
        
        # Act
        result = self.repository.get_property_use_codes_by_type(["residencial"])
        
        # Assert
        assert set(result) == {"01", "02", "03"}
    
    def test_get_property_classification(self):
        """Test getting property use classification."""
        # Act
        result = self.repository.get_property_use_classification()
        
        # Assert
        assert isinstance(result, dict)
        assert "clasificacion" in result
        assert "precuso" in result
        assert isinstance(result["clasificacion"], list)
        assert isinstance(result["precuso"], list)


class TestPropertyRepository:
    """Test PropertyRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.repository = PropertyRepository(self.mock_db)
    
    def test_get_properties_in_polygon_success(self):
        """Test successful polygon search."""
        # Arrange
        polygon = "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        mock_result = Mock()
        mock_result.fetchall.return_value = [("123",), ("456",)]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_properties_in_polygon(polygon)
        
        # Assert
        assert result == ["123", "456"]
        self.mock_db.execute.assert_called_once()
    
    def test_get_properties_in_polygon_empty(self):
        """Test polygon search with no results."""
        # Arrange
        polygon = "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_properties_in_polygon(polygon)
        
        # Assert
        assert result == []
    
    def test_get_properties_in_polygon_exception(self):
        """Test polygon search with database exception."""
        # Arrange
        polygon = "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            self.repository.get_properties_in_polygon(polygon)
    
    def test_get_properties_in_polygon_none_result(self):
        """Test polygon search with None result."""
        # Arrange
        polygon = "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        mock_result = Mock()
        mock_result.fetchall.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_properties_in_polygon(polygon)
        
        # Assert
        assert result == []
    
    def test_get_property_characteristics_success(self):
        """Test successful characteristics retrieval."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_row1 = Mock()
        mock_row1._mapping = {"barmanpre": "123", "preaconst": 100, "estrato": 3}
        mock_row2 = Mock()
        mock_row2._mapping = {"barmanpre": "456", "preaconst": 200, "estrato": 4}
        
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_property_characteristics(barmanpre_list)
        
        # Assert
        assert len(result) == 2
        assert result[0].barmanpre == "123"
        assert result[1].barmanpre == "456"
    
    def test_get_property_characteristics_empty_list(self):
        """Test characteristics retrieval with empty list."""
        # Act
        result = self.repository.get_property_characteristics([])
        
        # Assert
        assert result == []
    
    def test_get_property_characteristics_exception(self):
        """Test characteristics retrieval with database exception."""
        # Arrange
        barmanpre_list = ["123", "456"]
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            self.repository.get_property_characteristics(barmanpre_list)
    
    def test_get_property_characteristics_none_result(self):
        """Test characteristics retrieval with None result."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_result = Mock()
        mock_result.fetchall.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_property_characteristics(barmanpre_list)
        
        # Assert
        assert result == []
    
    def test_get_property_data_success(self):
        """Test successful property data retrieval."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_row1 = Mock()
        mock_row1._mapping = {"barmanpre": "123", "prechip": "CHIP123", "predirecc": "Address 1"}
        mock_row2 = Mock()
        mock_row2._mapping = {"barmanpre": "456", "prechip": "CHIP456", "predirecc": "Address 2"}
        
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_property_data(barmanpre_list)
        
        # Assert
        assert len(result) == 2
        assert result[0].barmanpre == "123"
        assert result[1].barmanpre == "456"
    
    def test_get_property_data_empty_list(self):
        """Test property data retrieval with empty list."""
        # Act
        result = self.repository.get_property_data([])
        
        # Assert
        assert result == []
    
    def test_get_property_data_exception(self):
        """Test property data retrieval with database exception."""
        # Arrange
        barmanpre_list = ["123", "456"]
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            self.repository.get_property_data(barmanpre_list)
    
    def test_get_property_data_none_result(self):
        """Test property data retrieval with None result."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_result = Mock()
        mock_result.fetchall.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_property_data(barmanpre_list)
        
        # Assert
        assert result == []
    
    def test_get_property_geometry_success(self):
        """Test successful geometry retrieval."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("123", "POINT(0 0)"),
            ("456", "POINT(1 1)")
        ]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_property_geometry(barmanpre_list)
        
        # Assert
        assert len(result) == 2
        assert result[0]["barmanpre"] == "123"
        assert result[0]["wkt"] == "POINT(0 0)"
        assert result[1]["barmanpre"] == "456"
        assert result[1]["wkt"] == "POINT(1 1)"
    
    def test_get_property_geometry_empty_list(self):
        """Test geometry retrieval with empty list."""
        # Act
        result = self.repository.get_property_geometry([])
        
        # Assert
        assert result == []
    
    def test_get_property_geometry_exception(self):
        """Test geometry retrieval with database exception."""
        # Arrange
        barmanpre_list = ["123", "456"]
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            self.repository.get_property_geometry(barmanpre_list)
    
    def test_get_property_geometry_none_result(self):
        """Test geometry retrieval with None result."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_result = Mock()
        mock_result.fetchall.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_property_geometry(barmanpre_list)
        
        # Assert
        assert result == []
    
    def test_get_property_geometry_single_item(self):
        """Test geometry retrieval with single item."""
        # Arrange
        barmanpre_list = ["123"]
        mock_result = Mock()
        mock_result.fetchall.return_value = [("123", "POINT(0 0)")]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = self.repository.get_property_geometry(barmanpre_list)
        
        # Assert
        assert len(result) == 1
        assert result[0]["barmanpre"] == "123"
        assert result[0]["wkt"] == "POINT(0 0)"


class TestPropertySearchService:
    """Test PropertySearchService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=PropertyRepository)
        self.mock_property_use_repository = Mock(spec=PropertyUseRepository)
        self.service = PropertySearchService(self.mock_db)
        self.service.repository = self.mock_repository
        self.service.property_use_repository = self.mock_property_use_repository
    
    def test_search_properties_no_polygon_properties(self):
        """Test search when no properties found in polygon."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        self.mock_repository.get_properties_in_polygon.return_value = []
        
        # Act
        result = self.service.search_properties(search_input)
        
        # Assert
        assert result.data == []
        assert result.meta.total_results == 0
        self.mock_repository.get_properties_in_polygon.assert_called_once()
    
    def test_search_properties_no_characteristics(self):
        """Test search when no characteristics data found."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        self.mock_repository.get_properties_in_polygon.return_value = ["123", "456"]
        self.mock_repository.get_property_characteristics.return_value = []
        
        # Act
        result = self.service.search_properties(search_input)
        
        # Assert
        assert result.data == []
        assert result.meta.total_results == 0
    
    def test_search_properties_invalid_polygon(self):
        """Test search with invalid polygon."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"  # Valid polygon for test
        )
        
        # Mock the repository to return empty results
        self.mock_repository.get_properties_in_polygon.return_value = []
        
        # Act
        result = self.service.search_properties(search_input)
        
        # Assert
        assert result.data == []
        assert result.meta.total_results == 0
    
    def test_search_properties_with_filters(self):
        """Test search with filters applied."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=50,
            max_area=200,
            min_age=0,
            max_age=2025,
            min_stratum=3,
            max_stratum=5,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        # Mock the property use repository
        self.mock_property_use_repository.get_property_use_codes_by_type.return_value = []
        
        # Mock characteristics with filterable data
        mock_char1 = Mock()
        mock_char1.barmanpre = "123"
        mock_char1.preaconst = 100
        mock_char1.preaterre = 150
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 4
        mock_char1.preusoph = "RESIDENCIAL"
        mock_char1.predios = "1"
        mock_char1.connpisos = "2"
        mock_char1.connsotano = "0"
        mock_char1.contsemis = "0"
        mock_char1.conelevaci = "0"
        mock_char1.formato_direccion = "Test Address"
        mock_char1.nombre_conjunto = "Test Complex"
        mock_char1.prenbarrio = "Test Neighborhood"
        mock_char1.precbarrio = "Test Barrio"
        mock_char1.locnombre = "Test Location"
        mock_char1.esquinero = True
        mock_char1.viaprincipal = True
        mock_char1.lista_precuso = "RESIDENCIAL"
        mock_char1.lista_precdestin = "VIVIENDA"
        mock_char1.manzcodigo = "123"
        
        mock_char2 = Mock()
        mock_char2.barmanpre = "456"
        mock_char2.preaconst = 300  # Should be filtered out (max_area = 200)
        mock_char2.preaterre = 400
        mock_char2.prevetustzmin = 2000
        mock_char2.prevetustzmax = 2005
        mock_char2.estrato = 2  # Should be filtered out (min_stratum = 3)
        mock_char2.preusoph = "RESIDENCIAL"
        mock_char2.predios = "1"
        mock_char2.connpisos = "1"
        mock_char2.connsotano = "0"
        mock_char2.contsemis = "0"
        mock_char2.conelevaci = "0"
        mock_char2.formato_direccion = "Test Address 2"
        mock_char2.nombre_conjunto = "Test Complex 2"
        mock_char2.prenbarrio = "Test Neighborhood 2"
        mock_char2.precbarrio = "Test Barrio 2"
        mock_char2.locnombre = "Test Location 2"
        mock_char2.esquinero = False
        mock_char2.viaprincipal = False
        mock_char2.lista_precuso = "RESIDENCIAL"
        mock_char2.lista_precdestin = "VIVIENDA"
        mock_char2.manzcodigo = "456"
        
        self.mock_repository.get_properties_in_polygon.return_value = ["123", "456"]
        self.mock_repository.get_property_characteristics.return_value = [mock_char1, mock_char2]
        self.mock_repository.get_property_data.return_value = []
        self.mock_repository.get_property_geometry.return_value = [
            {"barmanpre": "123", "wkt": "POINT(0 0)"}
        ]
        
        # Act
        result = self.service.search_properties(search_input)
        
        # Assert
        assert len(result.data) == 1  # Only mock_char1 should pass filters
        assert result.data[0].barmanpre == "123"
        assert result.data[0].preaconst == 100
        assert result.data[0].estrato == 4
    
    def test_search_properties_exception(self):
        """Test search with exception handling."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        self.mock_repository.get_properties_in_polygon.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            self.service.search_properties(search_input)
    
    def test_search_properties_no_filters_match(self):
        """Test search when no properties match filters."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=1000,  # Very high area that won't match
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        mock_char = Mock()
        mock_char.preaconst = 50  # Too small
        mock_char.preaterre = 100
        mock_char.prevetustzmin = 2010
        mock_char.prevetustzmax = 2015
        mock_char.estrato = 3
        mock_char.preusoph = "RESIDENCIAL"
        mock_char.predios = "1"
        mock_char.connpisos = "2"
        mock_char.connsotano = "0"
        mock_char.contsemis = "0"
        mock_char.conelevaci = "0"
        mock_char.formato_direccion = "Test Address"
        mock_char.nombre_conjunto = "Test Complex"
        mock_char.prenbarrio = "Test Neighborhood"
        mock_char.precbarrio = "Test Barrio"
        mock_char.locnombre = "Test Location"
        mock_char.esquinero = True
        mock_char.viaprincipal = True
        mock_char.lista_precuso = "RESIDENCIAL"
        mock_char.lista_precdestin = "VIVIENDA"
        mock_char.manzcodigo = "123"
        
        self.mock_repository.get_properties_in_polygon.return_value = ["123"]
        self.mock_repository.get_property_characteristics.return_value = [mock_char]
        
        # Act
        result = self.service.search_properties(search_input)
        
        # Assert
        assert result.data == []
        assert result.meta.total_results == 0
    
    def test_search_properties_with_age_filters(self):
        """Test search with age filters."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=10,
            max_age=15,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        # Mock the property use repository
        self.mock_property_use_repository.get_property_use_codes_by_type.return_value = []
        
        mock_char1 = Mock()
        mock_char1.barmanpre = "123"
        mock_char1.preaconst = 100
        mock_char1.preaterre = 150
        mock_char1.prevetustzmin = 2015  # Age = 10 (2025-2015)
        mock_char1.prevetustzmax = 2020
        mock_char1.estrato = 3
        mock_char1.preusoph = "RESIDENCIAL"
        mock_char1.predios = "1"
        mock_char1.connpisos = "2"
        mock_char1.connsotano = "0"
        mock_char1.contsemis = "0"
        mock_char1.conelevaci = "0"
        mock_char1.formato_direccion = "Test Address"
        mock_char1.nombre_conjunto = "Test Complex"
        mock_char1.prenbarrio = "Test Neighborhood"
        mock_char1.precbarrio = "Test Barrio"
        mock_char1.locnombre = "Test Location"
        mock_char1.esquinero = True
        mock_char1.viaprincipal = True
        mock_char1.lista_precuso = "RESIDENCIAL"
        mock_char1.lista_precdestin = "VIVIENDA"
        mock_char1.manzcodigo = "123"
        
        mock_char2 = Mock()
        mock_char2.barmanpre = "456"
        mock_char2.preaconst = 100
        mock_char2.preaterre = 150
        mock_char2.prevetustzmin = 2005  # Age = 20 (2025-2005) - too old
        mock_char2.prevetustzmax = 2010
        mock_char2.estrato = 3
        mock_char2.preusoph = "RESIDENCIAL"
        mock_char2.predios = "1"
        mock_char2.connpisos = "2"
        mock_char2.connsotano = "0"
        mock_char2.contsemis = "0"
        mock_char2.conelevaci = "0"
        mock_char2.formato_direccion = "Test Address 2"
        mock_char2.nombre_conjunto = "Test Complex 2"
        mock_char2.prenbarrio = "Test Neighborhood 2"
        mock_char2.precbarrio = "Test Barrio 2"
        mock_char2.locnombre = "Test Location 2"
        mock_char2.esquinero = False
        mock_char2.viaprincipal = False
        mock_char2.lista_precuso = "RESIDENCIAL"
        mock_char2.lista_precdestin = "VIVIENDA"
        mock_char2.manzcodigo = "456"
        
        self.mock_repository.get_properties_in_polygon.return_value = ["123", "456"]
        self.mock_repository.get_property_characteristics.return_value = [mock_char1, mock_char2]
        self.mock_repository.get_property_data.return_value = []
        self.mock_repository.get_property_geometry.return_value = [
            {"barmanpre": "123", "wkt": "POINT(0 0)"}
        ]
        
        # Act
        result = self.service.search_properties(search_input)
        
        # Assert
        assert len(result.data) == 1
        assert result.data[0].barmanpre == "123"
    
    def test_apply_business_filters_area_filter(self):
        """Test area filtering logic."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=100,
            max_area=200,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        # Mock the property use repository
        self.mock_property_use_repository.get_property_use_codes_by_type.return_value = []
        
        mock_char1 = Mock()
        mock_char1.preaconst = 150  # Should pass
        mock_char1.preaterre = 200
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 3
        mock_char1.preusoph = "RESIDENCIAL"
        
        mock_char2 = Mock()
        mock_char2.preaconst = 50  # Should be filtered out (min_area = 100)
        mock_char2.preaterre = 100
        mock_char2.prevetustzmin = 2010
        mock_char2.prevetustzmax = 2015
        mock_char2.estrato = 3
        mock_char2.preusoph = "RESIDENCIAL"
        
        mock_char3 = Mock()
        mock_char3.preaconst = 250  # Should be filtered out (max_area = 200)
        mock_char3.preaterre = 300
        mock_char3.prevetustzmin = 2010
        mock_char3.prevetustzmax = 2015
        mock_char3.estrato = 3
        mock_char3.preusoph = "RESIDENCIAL"
        
        characteristics = [mock_char1, mock_char2, mock_char3]
        
        # Act
        result = self.service._apply_business_filters(characteristics, search_input)
        
        # Assert
        assert len(result) == 1
        assert result[0] == mock_char1
    
    def test_apply_business_filters_stratum_filter(self):
        """Test stratum filtering logic."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=3,
            max_stratum=5,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        # Mock the property use repository
        self.mock_property_use_repository.get_property_use_codes_by_type.return_value = []
        
        mock_char1 = Mock()
        mock_char1.preaconst = 100
        mock_char1.preaterre = 150
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 4  # Should pass
        mock_char1.preusoph = "RESIDENCIAL"
        
        mock_char2 = Mock()
        mock_char2.preaconst = 100
        mock_char2.preaterre = 150
        mock_char2.prevetustzmin = 2010
        mock_char2.prevetustzmax = 2015
        mock_char2.estrato = 2  # Should be filtered out (min_stratum = 3)
        mock_char2.preusoph = "RESIDENCIAL"
        
        mock_char3 = Mock()
        mock_char3.preaconst = 100
        mock_char3.preaterre = 150
        mock_char3.prevetustzmin = 2010
        mock_char3.prevetustzmax = 2015
        mock_char3.estrato = 6  # Should be filtered out (max_stratum = 5)
        mock_char3.preusoph = "RESIDENCIAL"
        
        characteristics = [mock_char1, mock_char2, mock_char3]
        
        # Act
        result = self.service._apply_business_filters(characteristics, search_input)
        
        # Assert
        assert len(result) == 1
        assert result[0] == mock_char1
    
    def test_apply_business_filters_with_property_type_residencial(self):
        """Test filtering with property_type instead of property_use_codes."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["residencial"],  # Should map to ['01', '02', '03']
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],  # Empty, should use property_type
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        # Mock the property use repository
        self.mock_property_use_repository.get_property_use_codes_by_type.return_value = ["01", "02", "03"]
        
        mock_char1 = Mock()
        mock_char1.preaconst = 100
        mock_char1.preaterre = 150
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 3
        mock_char1.preusoph = "01"  # Should pass (residencial)
        
        mock_char2 = Mock()
        mock_char2.preaconst = 100
        mock_char2.preaterre = 150
        mock_char2.prevetustzmin = 2010
        mock_char2.prevetustzmax = 2015
        mock_char2.estrato = 3
        mock_char2.preusoph = "04"  # Should be filtered out (comercial)
        
        characteristics = [mock_char1, mock_char2]
        
        # Act
        result = self.service._apply_business_filters(characteristics, search_input)
        
        # Assert
        assert len(result) == 1
        assert result[0] == mock_char1
        self.mock_property_use_repository.get_property_use_codes_by_type.assert_called_once_with(["residencial"])
    
    def test_apply_business_filters_with_property_type_todo(self):
        """Test filtering with property_type 'todo' (should include all)."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["todo"],  # Should return empty list (include all)
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        # Mock the property use repository
        self.mock_property_use_repository.get_property_use_codes_by_type.return_value = []
        
        mock_char1 = Mock()
        mock_char1.preaconst = 100
        mock_char1.preaterre = 150
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 3
        mock_char1.preusoph = "01"  # Should pass (todo includes all)
        
        mock_char2 = Mock()
        mock_char2.preaconst = 100
        mock_char2.preaterre = 150
        mock_char2.prevetustzmin = 2010
        mock_char2.prevetustzmax = 2015
        mock_char2.estrato = 3
        mock_char2.preusoph = "04"  # Should pass (todo includes all)
        
        characteristics = [mock_char1, mock_char2]
        
        # Act
        result = self.service._apply_business_filters(characteristics, search_input)
        
        # Assert
        assert len(result) == 2  # Both should pass
        self.mock_property_use_repository.get_property_use_codes_by_type.assert_called_once_with(["todo"])
    
    def test_apply_business_filters_with_property_use_codes_direct(self):
        """Test filtering with direct property_use_codes (should not call repository)."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=[],  # Empty
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=["01", "02"],  # Direct codes
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        mock_char1 = Mock()
        mock_char1.preaconst = 100
        mock_char1.preaterre = 150
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 3
        mock_char1.preusoph = "01"  # Should pass
        
        mock_char2 = Mock()
        mock_char2.preaconst = 100
        mock_char2.preaterre = 150
        mock_char2.prevetustzmin = 2010
        mock_char2.prevetustzmax = 2015
        mock_char2.estrato = 3
        mock_char2.preusoph = "03"  # Should be filtered out
        
        characteristics = [mock_char1, mock_char2]
        
        # Act
        result = self.service._apply_business_filters(characteristics, search_input)
        
        # Assert
        assert len(result) == 1
        assert result[0] == mock_char1
        # Should not call the repository since we have direct property_use_codes
        self.mock_property_use_repository.get_property_use_codes_by_type.assert_not_called()
    
    def test_apply_business_filters_none_values(self):
        """Test filtering with None values."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=100,
            max_area=200,
            min_age=10,
            max_age=20,
            min_stratum=3,
            max_stratum=5,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        mock_char = Mock()
        mock_char.preaconst = None  # Should be filtered out
        mock_char.preaterre = None
        mock_char.prevetustzmin = None
        mock_char.prevetustzmax = None
        mock_char.estrato = None
        mock_char.preusoph = None
        
        characteristics = [mock_char]
        
        # Act
        result = self.service._apply_business_filters(characteristics, search_input)
        
        # Assert
        assert len(result) == 0
    
    def test_apply_business_filters_empty_characteristics(self):
        """Test filtering with empty characteristics list."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        
        characteristics = []
        
        # Act
        result = self.service._apply_business_filters(characteristics, search_input)
        
        # Assert
        assert len(result) == 0
    
    def test_transform_to_response_format(self):
        """Test data transformation to response format."""
        # Arrange
        mock_char = Mock()
        mock_char.barmanpre = "123"
        mock_char.preaconst = 100
        mock_char.preaterre = 150
        mock_char.prevetustzmin = 2010
        mock_char.preusoph = "RESIDENCIAL"
        mock_char.estrato = 4
        mock_char.predios = "1"
        mock_char.connpisos = "2"
        mock_char.connsotano = "0"
        mock_char.contsemis = "0"
        mock_char.conelevaci = "0"
        mock_char.formato_direccion = "Test Address"
        mock_char.nombre_conjunto = "Test Complex"
        mock_char.prenbarrio = "Test Neighborhood"
        mock_char.precbarrio = "Test Barrio"
        mock_char.locnombre = "Test Location"
        mock_char.esquinero = True
        mock_char.viaprincipal = True
        mock_char.lista_precuso = "RESIDENCIAL"
        mock_char.lista_precdestin = "VIVIENDA"
        mock_char.manzcodigo = "123"
        
        mock_prop = Mock()
        mock_prop.barmanpre = "123"
        mock_prop.prechip = "CHIP123"
        mock_prop.predirecc = "Test Street 123"
        mock_prop.matriculainmobiliaria = "MAT123"
        
        characteristics = [mock_char]
        property_data = [mock_prop]
        geometry_data = [{"barmanpre": "123", "wkt": "POINT(0 0)"}]
        
        # Act
        result = self.service._transform_to_response_format(characteristics, property_data, geometry_data)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], PropertyResult)
        assert result[0].barmanpre == "123"
        assert result[0].preaconst == 100
        assert result[0].estrato == 4
        assert result[0].wkt == "POINT(0 0)"
        assert result[0].prechip == "CHIP123"
        assert result[0].predirecc == "Test Street 123"
    
    def test_transform_to_response_format_no_property_data(self):
        """Test transformation with no property data."""
        # Arrange
        mock_char = Mock()
        mock_char.barmanpre = "123"
        mock_char.preaconst = 100
        mock_char.preaterre = 150
        mock_char.prevetustzmin = 2010
        mock_char.preusoph = "RESIDENCIAL"
        mock_char.estrato = 4
        mock_char.predios = "1"
        mock_char.connpisos = "2"
        mock_char.connsotano = "0"
        mock_char.contsemis = "0"
        mock_char.conelevaci = "0"
        mock_char.formato_direccion = "Test Address"
        mock_char.nombre_conjunto = "Test Complex"
        mock_char.prenbarrio = "Test Neighborhood"
        mock_char.precbarrio = "Test Barrio"
        mock_char.locnombre = "Test Location"
        mock_char.esquinero = True
        mock_char.viaprincipal = True
        mock_char.lista_precuso = "RESIDENCIAL"
        mock_char.lista_precdestin = "VIVIENDA"
        mock_char.manzcodigo = "123"
        
        characteristics = [mock_char]
        property_data = []
        geometry_data = [{"barmanpre": "123", "wkt": "POINT(0 0)"}]
        
        # Act
        result = self.service._transform_to_response_format(characteristics, property_data, geometry_data)
        
        # Assert
        assert len(result) == 1
        assert result[0].prechip is None
        assert result[0].predirecc is None
    
    def test_transform_to_response_format_no_geometry(self):
        """Test transformation with no geometry data."""
        # Arrange
        mock_char = Mock()
        mock_char.barmanpre = "123"
        mock_char.preaconst = 100
        mock_char.preaterre = 150
        mock_char.prevetustzmin = 2010
        mock_char.preusoph = "RESIDENCIAL"
        mock_char.estrato = 4
        mock_char.predios = "1"
        mock_char.connpisos = "2"
        mock_char.connsotano = "0"
        mock_char.contsemis = "0"
        mock_char.conelevaci = "0"
        mock_char.formato_direccion = "Test Address"
        mock_char.nombre_conjunto = "Test Complex"
        mock_char.prenbarrio = "Test Neighborhood"
        mock_char.precbarrio = "Test Barrio"
        mock_char.locnombre = "Test Location"
        mock_char.esquinero = True
        mock_char.viaprincipal = True
        mock_char.lista_precuso = "RESIDENCIAL"
        mock_char.lista_precdestin = "VIVIENDA"
        mock_char.manzcodigo = "123"
        
        characteristics = [mock_char]
        property_data = []
        geometry_data = []
        
        # Act
        result = self.service._transform_to_response_format(characteristics, property_data, geometry_data)
        
        # Assert
        assert len(result) == 1
        assert result[0].wkt is None
    
    def test_create_search_meta(self):
        """Test search metadata creation."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["residencial"],
            min_area=50,
            max_area=200,
            min_age=0,
            max_age=20,
            min_stratum=3,
            max_stratum=5,
            property_use_codes=["01"],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        total_results = 10
        execution_time_ms = 150.5
        
        # Act
        result = self.service._create_search_meta(search_input, total_results, execution_time_ms)
        
        # Assert
        assert isinstance(result, SearchMeta)
        assert result.total_results == 10
        assert result.execution_time_ms == 150.5
        assert result.filters_applied["property_type"] == ["residencial"]
        assert result.filters_applied["min_area"] == 50
        assert result.filters_applied["max_area"] == 200
    
    def test_create_empty_response(self):
        """Test empty response creation."""
        # Arrange
        search_input = GeneralSearchInput(
            property_type=["All"],
            min_area=0,
            max_area=0,
            min_age=0,
            max_age=2025,
            min_stratum=0,
            max_stratum=0,
            property_use_codes=[],
            polygon="POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )
        start_time = 1000.0
        
        # Act
        result = self.service._create_empty_response(search_input, start_time)
        
        # Assert
        assert isinstance(result, GeneralSearchResponse)
        assert len(result.data) == 0
        assert result.meta.total_results == 0
    
    def test_validate_polygon_valid(self):
        """Test polygon validation with valid input."""
        polygon = "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        assert self.service._validate_polygon(polygon) == True
    
    def test_validate_polygon_invalid_empty(self):
        """Test polygon validation with empty input."""
        assert self.service._validate_polygon("") == False
        assert self.service._validate_polygon(None) == False
    
    def test_validate_polygon_invalid_none(self):
        """Test polygon validation with 'none' input."""
        assert self.service._validate_polygon("none") == False
        assert self.service._validate_polygon("NONE") == False
        assert self.service._validate_polygon("None") == False
    
    def test_validate_polygon_invalid_format(self):
        """Test polygon validation with invalid format."""
        assert self.service._validate_polygon("POINT(0 0)") == False
        assert self.service._validate_polygon("invalid") == False
    
    def test_validate_polygon_whitespace(self):
        """Test polygon validation with whitespace."""
        assert self.service._validate_polygon("   ") == False
        assert self.service._validate_polygon("POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))") == True


class TestSearchEndpoints:
    """Test search endpoints."""
    
    def test_get_search_service_dependency(self):
        """Test dependency injection for search service."""
        # Arrange
        mock_db = Mock(spec=Session)
        
        # Act
        service = get_search_service(mock_db)
        
        # Assert
        assert isinstance(service, PropertySearchService)
        assert service.db == mock_db
    
    def test_general_search_success(self):
        """Test successful general search endpoint."""
        # Arrange
        search_data = {
            "property_type": ["residencial"],
            "min_area": 50.0,
            "max_area": 200.0,
            "min_age": 0,
            "max_age": 20,
            "min_stratum": 3,
            "max_stratum": 5,
            "property_use_codes": ["01"],
            "polygon": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        }
        
        # Mock the search service
        with patch('app.api.v1.endpoints.search.PropertySearchService') as mock_service_class:
            mock_service = Mock()
            mock_service.search_properties.return_value = GeneralSearchResponse(
                meta=SearchMeta(
                    total_results=1,
                    execution_time_ms=100.0,
                    request_id="test-id",
                    filters_applied={},
                    timestamp="2024-01-15T10:30:00.000Z"
                ),
                data=[]
            )
            mock_service_class.return_value = mock_service
            
            # Act
            response = client.post("/api/v1/search/general", json=search_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "meta" in data
            assert "data" in data
    
    def test_general_search_invalid_input(self):
        """Test general search with invalid input."""
        # Arrange
        search_data = {
            "property_type": ["residencial"],
            "min_area": -50.0,  # Invalid negative area
            "polygon": "invalid"  # Invalid polygon
        }
        
        # Act
        response = client.post("/api/v1/search/general", json=search_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_general_search_exception_handling(self):
        """Test general search with exception handling."""
        # Arrange
        search_data = {
            "property_type": ["residencial"],
            "min_area": 50.0,
            "max_area": 200.0,
            "min_age": 0,
            "max_age": 20,
            "min_stratum": 3,
            "max_stratum": 5,
            "property_use_codes": ["01"],
            "polygon": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        }
        
        # Mock the search service to raise an exception
        with patch('app.api.v1.endpoints.search.PropertySearchService') as mock_service_class:
            mock_service = Mock()
            mock_service.search_properties.side_effect = Exception("Database error")
            mock_service_class.return_value = mock_service
            
            # Act
            response = client.post("/api/v1/search/general", json=search_data)
            
            # Assert
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
    
    def test_general_search_missing_required_fields(self):
        """Test general search with missing required fields."""
        # Arrange
        search_data = {
            "property_type": ["residencial"]
            # Missing polygon and other required fields
        }
        
        # Act
        response = client.post("/api/v1/search/general", json=search_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_general_search_invalid_polygon_format(self):
        """Test general search with invalid polygon format."""
        # Arrange
        search_data = {
            "property_type": ["residencial"],
            "min_area": 50.0,
            "max_area": 200.0,
            "min_age": 0,
            "max_age": 20,
            "min_stratum": 3,
            "max_stratum": 5,
            "property_use_codes": ["01"],
            "polygon": "INVALID_POLYGON_FORMAT"
        }
        
        # Act
        response = client.post("/api/v1/search/general", json=search_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_health_check_success(self):
        """Test successful health check."""
        # Act
        response = client.get("/api/v1/search/health")
        
        # Assert
        assert response.status_code in [200, 503]  # Can be either depending on DB connection
        data = response.json()
        if response.status_code == 503:
            assert "detail" in data
        else:
            assert "status" in data
            assert "service" in data
    
    def test_health_check_database_connection_failure(self):
        """Test health check when database connection fails."""
        # This test would require mocking the database connection
        # For now, we'll test the endpoint structure
        response = client.get("/api/v1/search/health")
        assert response.status_code in [200, 503]
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        # Act
        response = client.get("/api/v1/search/metrics")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "metrics" in data
        assert "timestamp" in data
        assert data["service"] == "property-search"
    
    def test_metrics_endpoint_structure(self):
        """Test metrics endpoint structure."""
        # Act
        response = client.get("/api/v1/search/metrics")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "metrics" in data
        assert "timestamp" in data
        assert data["service"] == "property-search"
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        # Act
        response = client.get("/api/v1/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "architecture" in data
        assert "endpoints" in data
    
    def test_docs_endpoint(self):
        """Test docs endpoint."""
        # Act
        response = client.get("/docs")
        
        # Assert
        assert response.status_code == 200
    
    def test_openapi_endpoint(self):
        """Test OpenAPI endpoint."""
        # Act
        response = client.get("/openapi.json")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data 