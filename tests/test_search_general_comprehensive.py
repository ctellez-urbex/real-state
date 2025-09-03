"""
Comprehensive Test Suite for /general Search Endpoint
Target: 98% Coverage

This test suite provides comprehensive coverage for:
- API endpoint testing
- Service layer testing
- Repository layer testing
- Schema validation testing
- Error handling testing
- Integration testing
"""

import uuid
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.endpoints.search import get_search_service
from app.main import app
from app.models import BogotaDataCaracteristicas
from app.repositories.property import PropertyRepository
from app.schemas.search import (
    PropertyResponse,
    ResponseMeta,
    SearchRequest,
    SearchResponse,
)
from app.services.property_search import PropertySearch

# Test client will be created in each test method to avoid initialization issues

# Test constants
VALID_POLYGON = "POLYGON ((-74.052562 4.690891, -74.052765 4.689811, -74.051499 4.689608, -74.051285 4.690773, -74.052562 4.690891))"
INVALID_POLYGON = "INVALID_POLYGON_FORMAT"
VALID_API_KEY = "urbex-test-key-vjtyZHsCM2VpR_iGptzRxw"


class TestSearchEndpointIntegration:
    """Integration tests for the /general search endpoint."""

    def test_general_search_success_with_results(self):
        """Test successful search with valid polygon returning results."""
        # Arrange
        client = TestClient(app)
        payload = {"tipoinmueble": ["Todos"], "polygon": VALID_POLYGON, "limit": 5}
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total" in data
        assert "meta" in data
        assert "timestamp" in data["meta"]
        assert "request_id" in data["meta"]
        assert "filters_applied" in data["meta"]

    def test_general_search_empty_results(self):
        """Test search with polygon that returns no results."""
        # Arrange - polygon in area with no properties
        client = TestClient(app)
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": "POLYGON ((0 0, 0.001 0, 0.001 0.001, 0 0.001, 0 0))",
            "limit": 10,
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 0
        assert len(data["data"]) == 0

    def test_general_search_with_filters(self):
        """Test search with various filters applied."""
        # Arrange
        client = TestClient(app)
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": VALID_POLYGON,
            "areamin": 50,
            "areamax": 500,
            "estratomin": 3,
            "estratomax": 6,
            "antiguedadmin": 0,
            "antiguedadmax": 2023,
            "limit": 10,
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "areamin" in data["meta"]["filters_applied"]
        assert "estratomin" in data["meta"]["filters_applied"]

    def test_general_search_pagination(self):
        """Test search with pagination parameters."""
        # Arrange
        client = TestClient(app)
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": VALID_POLYGON,
            "limit": 3,
            "offset": 0,
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 3
        assert data["offset"] == 0

    def test_general_search_missing_api_key(self):
        """Test search without API key (should fail)."""
        # Arrange
        client = TestClient(app)
        payload = {"tipoinmueble": ["Todos"], "polygon": VALID_POLYGON}

        # Act
        response = client.post("/api/v1/search/general", json=payload)

        # Assert
        assert response.status_code == 403  # Forbidden without API key

    def test_general_search_invalid_api_key(self):
        """Test search with invalid API key."""
        # Arrange
        client = TestClient(app)
        payload = {"tipoinmueble": ["Todos"], "polygon": VALID_POLYGON}
        headers = {"Content-Type": "application/json", "x-api-key": "invalid-key"}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 403  # Forbidden with invalid key

    def test_general_search_invalid_polygon_format(self):
        """Test search with invalid polygon format."""
        # Arrange
        client = TestClient(app)
        payload = {"tipoinmueble": ["Todos"], "polygon": INVALID_POLYGON}
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_general_search_invalid_parameters(self):
        """Test search with invalid parameter values."""
        # Arrange
        client = TestClient(app)
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": VALID_POLYGON,
            "areamin": -50,  # Invalid negative area
            "limit": -1,  # Invalid negative limit
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_general_search_malformed_json(self):
        """Test search with malformed JSON."""
        # Arrange
        client = TestClient(app)
        malformed_json = '{"tipoinmueble": ["Todos", "polygon": invalid}'
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post(
            "/api/v1/search/general", data=malformed_json, headers=headers
        )

        # Assert
        assert response.status_code == 422  # JSON decode error


class TestPropertySearch:
    """Unit tests for PropertySearch."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=PropertyRepository)
        self.service = PropertySearch(self.mock_db)
        self.service.repository = self.mock_repository

    def test_search_properties_successful_flow(self):
        """Test successful search flow with mocked dependencies."""
        # Arrange
        search_input = SearchRequest(
            tipoinmueble=["Todos"], polygon=VALID_POLYGON, limit=10
        )
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Mock repository responses
        self.mock_repository.get_properties_in_polygon.return_value = ["123", "456"]

        # Mock characteristics
        mock_char1 = Mock(spec=BogotaDataCaracteristicas)
        mock_char1.id = 123
        mock_char1.barmanpre = "123"
        mock_char1.preaconst = 100.0
        mock_char1.preaterre = 150.0
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 3.0
        mock_char1.predios = 1
        mock_char1.connpisos = 2.0
        mock_char1.connsotano = 0.0
        mock_char1.contsemis = 0.0
        mock_char1.conelevaci = 0.0
        mock_char1.formato_direccion = "Test Address 1"
        mock_char1.nombre_conjunto = "Test Complex 1"
        mock_char1.prenbarrio = "Test Neighborhood 1"
        mock_char1.precbarrio = "123"
        mock_char1.locnombre = "Test Location 1"
        mock_char1.preusoph = "S"
        mock_char1.manzcodigo = "123"
        mock_char1.esquinero = 1.0
        mock_char1.viaprincipal = 0.0
        mock_char1.lista_precuso = "01"
        mock_char1.lista_precdestin = "01"

        mock_char2 = Mock(spec=BogotaDataCaracteristicas)
        mock_char2.id = 456
        mock_char2.barmanpre = "456"
        mock_char2.preaconst = 200.0
        mock_char2.preaterre = 250.0
        mock_char2.prevetustzmin = 2000
        mock_char2.prevetustzmax = 2005
        mock_char2.estrato = 4.0
        mock_char2.predios = 1
        mock_char2.connpisos = 3.0
        mock_char2.connsotano = 1.0
        mock_char2.contsemis = 0.0
        mock_char2.conelevaci = 1.0
        mock_char2.formato_direccion = "Test Address 2"
        mock_char2.nombre_conjunto = "Test Complex 2"
        mock_char2.prenbarrio = "Test Neighborhood 2"
        mock_char2.precbarrio = "456"
        mock_char2.locnombre = "Test Location 2"
        mock_char2.preusoph = "S"
        mock_char2.manzcodigo = "456"
        mock_char2.esquinero = 0.0
        mock_char2.viaprincipal = 1.0
        mock_char2.lista_precuso = "02"
        mock_char2.lista_precdestin = "01"

        self.mock_repository.get_property_characteristics.return_value = [
            mock_char1,
            mock_char2,
        ]
        self.mock_repository.get_property_data.return_value = []
        self.mock_repository.get_property_geometry.return_value = [
            {"barmanpre": "123", "wkt": "POINT(0 0)"},
            {"barmanpre": "456", "wkt": "POINT(1 1)"},
        ]

        # Act
        result = self.service.search_properties(search_input, request_id, timestamp)

        # Assert
        assert isinstance(result, SearchResponse)
        assert result.success is True
        assert result.total == 2
        assert len(result.data) == 2
        assert result.meta.request_id == request_id
        assert "polygon" in result.meta.filters_applied

        # Verify repository calls
        self.mock_repository.get_properties_in_polygon.assert_called_once_with(
            VALID_POLYGON
        )
        self.mock_repository.get_property_characteristics.assert_called_once_with(
            ["123", "456"]
        )
        self.mock_repository.get_property_geometry.assert_called_once_with(
            ["123", "456"]
        )

    def test_search_properties_no_polygon_properties(self):
        """Test search when no properties found in polygon."""
        # Arrange
        search_input = SearchRequest(tipoinmueble=["Todos"], polygon=VALID_POLYGON)
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        self.mock_repository.get_properties_in_polygon.return_value = []

        # Act
        result = self.service.search_properties(search_input, request_id, timestamp)

        # Assert
        assert result.success is True
        assert result.total == 0
        assert len(result.data) == 0
        assert result.message == "No properties found matching the criteria"

    def test_search_properties_no_characteristics(self):
        """Test search when no characteristics found."""
        # Arrange
        search_input = SearchRequest(tipoinmueble=["Todos"], polygon=VALID_POLYGON)
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        self.mock_repository.get_properties_in_polygon.return_value = ["123", "456"]
        self.mock_repository.get_property_characteristics.return_value = []

        # Act
        result = self.service.search_properties(search_input, request_id, timestamp)

        # Assert
        assert result.success is True
        assert result.total == 0
        assert len(result.data) == 0

    def test_search_properties_with_area_filters(self):
        """Test search with area filters applied."""
        # Arrange
        search_input = SearchRequest(
            tipoinmueble=["Todos"], polygon=VALID_POLYGON, areamin=150, areamax=300
        )
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        self.mock_repository.get_properties_in_polygon.return_value = ["123", "456"]

        # Mock characteristics - one should pass filter, one should not
        mock_char1 = Mock(spec=BogotaDataCaracteristicas)
        mock_char1.id = 123
        mock_char1.barmanpre = "123"
        mock_char1.preaconst = 100.0  # Below minimum, should be filtered out
        mock_char1.preaterre = 150.0
        mock_char1.prevetustzmin = 2010
        mock_char1.prevetustzmax = 2015
        mock_char1.estrato = 3.0
        mock_char1.predios = 1
        mock_char1.connpisos = 2.0
        mock_char1.connsotano = 0.0
        mock_char1.contsemis = 0.0
        mock_char1.conelevaci = 0.0
        mock_char1.formato_direccion = "Test Address 1"
        mock_char1.nombre_conjunto = "Test Complex 1"
        mock_char1.prenbarrio = "Test Neighborhood 1"
        mock_char1.precbarrio = "123"
        mock_char1.locnombre = "Test Location 1"
        mock_char1.preusoph = "S"
        mock_char1.manzcodigo = "123"
        mock_char1.esquinero = 1.0
        mock_char1.viaprincipal = 0.0
        mock_char1.lista_precuso = "01"
        mock_char1.lista_precdestin = "01"

        mock_char2 = Mock(spec=BogotaDataCaracteristicas)
        mock_char2.id = 456
        mock_char2.barmanpre = "456"
        mock_char2.preaconst = 200.0  # Within range, should pass
        mock_char2.preaterre = 250.0
        mock_char2.prevetustzmin = 2000
        mock_char2.prevetustzmax = 2005
        mock_char2.estrato = 4.0
        mock_char2.predios = 1
        mock_char2.connpisos = 3.0
        mock_char2.connsotano = 1.0
        mock_char2.contsemis = 0.0
        mock_char2.conelevaci = 1.0
        mock_char2.formato_direccion = "Test Address 2"
        mock_char2.nombre_conjunto = "Test Complex 2"
        mock_char2.prenbarrio = "Test Neighborhood 2"
        mock_char2.precbarrio = "456"
        mock_char2.locnombre = "Test Location 2"
        mock_char2.preusoph = "S"
        mock_char2.manzcodigo = "456"
        mock_char2.esquinero = 0.0
        mock_char2.viaprincipal = 1.0
        mock_char2.lista_precuso = "02"
        mock_char2.lista_precdestin = "01"

        self.mock_repository.get_property_characteristics.return_value = [
            mock_char1,
            mock_char2,
        ]
        self.mock_repository.get_property_data.return_value = []
        self.mock_repository.get_property_geometry.return_value = [
            {"barmanpre": "456", "wkt": "POINT(1 1)"}
        ]

        # Act
        result = self.service.search_properties(search_input, request_id, timestamp)

        # Assert
        assert result.success is True
        assert result.total == 1  # Only one property should pass the filter
        assert len(result.data) == 1
        assert result.data[0].barmanpre == "456"

    def test_search_properties_database_error(self):
        """Test search with database error."""
        # Arrange
        search_input = SearchRequest(tipoinmueble=["Todos"], polygon=VALID_POLYGON)
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        self.mock_repository.get_properties_in_polygon.side_effect = SQLAlchemyError(
            "Database connection error"
        )

        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            self.service.search_properties(search_input, request_id, timestamp)

    def test_create_response_meta(self):
        """Test response metadata creation."""
        # Arrange
        search_input = SearchRequest(
            tipoinmueble=["Todos"], polygon=VALID_POLYGON, areamin=100, estratomin=3
        )
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Act
        meta = self.service._create_response_meta(search_input, request_id, timestamp)

        # Assert
        assert isinstance(meta, ResponseMeta)
        assert meta.request_id == request_id
        assert meta.timestamp == timestamp
        assert "polygon" in meta.filters_applied
        assert "areamin" in meta.filters_applied
        assert "estratomin" in meta.filters_applied


class TestPropertyRepository:
    """Unit tests for PropertyRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.repository = PropertyRepository(self.mock_db)

    def test_get_properties_in_polygon_success(self):
        """Test successful polygon search."""
        # Arrange
        polygon = VALID_POLYGON
        mock_result = Mock()
        mock_result.fetchall.return_value = [("123",), ("456",), ("789",)]
        self.mock_db.execute.return_value = mock_result

        # Act
        result = self.repository.get_properties_in_polygon(polygon)

        # Assert
        assert result == ["123", "456", "789"]
        self.mock_db.execute.assert_called_once()

    def test_get_properties_in_polygon_empty_result(self):
        """Test polygon search with no results."""
        # Arrange
        polygon = VALID_POLYGON
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        self.mock_db.execute.return_value = mock_result

        # Act
        result = self.repository.get_properties_in_polygon(polygon)

        # Assert
        assert result == []

    def test_get_properties_in_polygon_none_result(self):
        """Test polygon search with None result."""
        # Arrange
        polygon = VALID_POLYGON
        mock_result = Mock()
        mock_result.fetchall.return_value = None
        self.mock_db.execute.return_value = mock_result

        # Act
        result = self.repository.get_properties_in_polygon(polygon)

        # Assert
        assert result == []

    def test_get_properties_in_polygon_database_error(self):
        """Test polygon search with database error."""
        # Arrange
        polygon = VALID_POLYGON
        self.mock_db.execute.side_effect = SQLAlchemyError("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            self.repository.get_properties_in_polygon(polygon)

    def test_get_property_characteristics_success(self):
        """Test successful characteristics retrieval."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_row1 = Mock()
        mock_row1._mapping = {
            "barmanpre": "123",
            "preaconst": 100.0,
            "estrato": 3.0,
            "preaterre": 150.0,
            "prevetustzmin": 2010,
            "prevetustzmax": 2015,
            "predios": 1,
            "connpisos": 2.0,
            "connsotano": 0.0,
            "contsemis": 0.0,
            "conelevaci": 0.0,
            "formato_direccion": "Test Address",
            "nombre_conjunto": "Test Complex",
            "prenbarrio": "Test Neighborhood",
            "precbarrio": "123",
            "locnombre": "Test Location",
            "preusoph": "S",
            "manzcodigo": "123",
            "esquinero": 1.0,
            "viaprincipal": 0.0,
            "lista_precuso": "01",
            "lista_precdestin": "01",
        }

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row1]
        self.mock_db.execute.return_value = mock_result

        # Act
        result = self.repository.get_property_characteristics(barmanpre_list)

        # Assert
        assert len(result) == 1
        assert result[0].barmanpre == "123"
        assert result[0].preaconst == 100.0

    def test_get_property_characteristics_empty_list(self):
        """Test characteristics retrieval with empty list."""
        # Act
        result = self.repository.get_property_characteristics([])

        # Assert
        assert result == []

    def test_get_property_characteristics_database_error(self):
        """Test characteristics retrieval with database error."""
        # Arrange
        barmanpre_list = ["123", "456"]
        self.mock_db.execute.side_effect = SQLAlchemyError("Database error")

        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            self.repository.get_property_characteristics(barmanpre_list)

    def test_get_property_geometry_success(self):
        """Test successful geometry retrieval."""
        # Arrange
        barmanpre_list = ["123", "456"]
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("123", "POINT(-74.0527 4.6905)"),
            (
                "456",
                "POLYGON((-74.0530 4.6900, -74.0525 4.6900, -74.0525 4.6905, -74.0530 4.6905, -74.0530 4.6900))",
            ),
        ]
        self.mock_db.execute.return_value = mock_result

        # Act
        result = self.repository.get_property_geometry(barmanpre_list)

        # Assert
        assert len(result) == 2
        assert result[0]["barmanpre"] == "123"
        assert result[0]["wkt"] == "POINT(-74.0527 4.6905)"
        assert result[1]["barmanpre"] == "456"

    def test_get_property_geometry_empty_list(self):
        """Test geometry retrieval with empty list."""
        # Act
        result = self.repository.get_property_geometry([])

        # Assert
        assert result == []

    def test_get_property_geometry_database_error(self):
        """Test geometry retrieval with database error."""
        # Arrange
        barmanpre_list = ["123", "456"]
        self.mock_db.execute.side_effect = SQLAlchemyError("Database error")

        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            self.repository.get_property_geometry(barmanpre_list)


class TestSearchSchemas:
    """Unit tests for search-related schemas."""

    def test_search_request_valid_data(self):
        """Test SearchRequest with valid data."""
        # Arrange & Act
        request = SearchRequest(
            tipoinmueble=["Todos"],
            polygon=VALID_POLYGON,
            areamin=50,
            areamax=500,
            estratomin=1,
            estratomax=6,
            limit=20,
            offset=0,
        )

        # Assert
        assert request.tipoinmueble == ["Todos"]
        assert request.polygon == VALID_POLYGON
        assert request.min_area == 50
        assert request.max_area == 500
        assert request.limit == 20
        assert request.offset == 0

    def test_search_request_validation_errors(self):
        """Test SearchRequest validation errors."""
        # Test negative area
        with pytest.raises(ValueError):
            SearchRequest(
                tipoinmueble=["Todos"],
                polygon=VALID_POLYGON,
                areamin=-50,  # Should fail
            )

        # Test max less than min
        with pytest.raises(ValueError):
            SearchRequest(
                tipoinmueble=["Todos"],
                polygon=VALID_POLYGON,
                areamin=500,
                areamax=100,  # Should fail: max < min
            )

    def test_search_request_aliases(self):
        """Test SearchRequest field aliases."""
        # Arrange & Act
        request_data = {
            "tipoinmueble": ["Todos"],
            "polygon": VALID_POLYGON,
            "areamin": 50,
            "areamax": 500,
            "antiguedadmin": 0,
            "antiguedadmax": 20,
            "estratomin": 1,
            "estratomax": 6,
        }
        request = SearchRequest(**request_data)

        # Assert
        dumped = request.model_dump(by_alias=True)
        assert "areamin" in dumped
        assert "antiguedadmin" in dumped
        assert "estratomin" in dumped

    def test_property_response_creation(self):
        """Test PropertyResponse creation."""
        # Arrange & Act
        property_response = PropertyResponse(
            id=12345,
            barmanpre="123456789",
            preaconst=150.5,
            preaterre=200.0,
            prevetustzmin=2010,
            prevetustzmax=2015,
            estrato=4.0,
            predios=1,
            formato_direccion="CL 100 # 15-20",
            locnombre="USAQUEN",
            wkt="POINT(-74.0527 4.6905)",
        )

        # Assert
        assert property_response.id == 12345
        assert property_response.barmanpre == "123456789"
        assert property_response.preaconst == 150.5
        assert property_response.wkt == "POINT(-74.0527 4.6905)"

    def test_search_response_creation(self):
        """Test SearchResponse creation."""
        # Arrange
        meta = ResponseMeta(
            timestamp=datetime.utcnow(),
            request_id=str(uuid.uuid4()),
            filters_applied={"polygon": VALID_POLYGON},
        )

        property_data = [
            PropertyResponse(
                id=123, barmanpre="123456789", preaconst=150.5, locnombre="USAQUEN"
            )
        ]

        # Act
        response = SearchResponse(
            success=True,
            message="Found 1 property",
            data=property_data,
            total=1,
            limit=100,
            offset=0,
            meta=meta,
        )

        # Assert
        assert response.success is True
        assert response.total == 1
        assert len(response.data) == 1
        assert response.meta.request_id == meta.request_id

    def test_response_meta_filters_applied(self):
        """Test ResponseMeta filters_applied functionality."""
        # Arrange & Act
        meta = ResponseMeta(
            timestamp=datetime.utcnow(),
            request_id=str(uuid.uuid4()),
            filters_applied={
                "polygon": VALID_POLYGON,
                "areamin": 50,
                "estratomin": 3,
                "tipoinmueble": ["Todos"],
            },
        )

        # Assert
        assert "polygon" in meta.filters_applied
        assert "areamin" in meta.filters_applied
        assert "estratomin" in meta.filters_applied
        assert meta.filters_applied["areamin"] == 50


class TestDependencyInjection:
    """Test dependency injection for the search endpoint."""

    def test_get_search_service_dependency(self):
        """Test dependency injection for search service."""
        # Arrange
        mock_db = Mock(spec=Session)

        # Act
        service = get_search_service(mock_db)

        # Assert
        assert isinstance(service, PropertySearch)
        assert service.db == mock_db


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_search_endpoint_exception_handling(self):
        """Test search endpoint with service exception."""
        # Arrange
        payload = {"tipoinmueble": ["Todos"], "polygon": VALID_POLYGON}
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Mock the service to raise an exception
        with patch("app.api.v1.endpoints.search.PropertySearch") as mock_service_class:
            client = TestClient(app)
            mock_service = Mock()
            mock_service.search_properties.side_effect = Exception(
                "Simulated database error"
            )
            mock_service_class.return_value = mock_service

            # Act
            response = client.post(
                "/api/v1/search/general", json=payload, headers=headers
            )

            # Assert
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_search_service_repository_exception(self):
        """Test search service with repository exception."""
        # Arrange
        mock_db = Mock(spec=Session)
        mock_repository = Mock(spec=PropertyRepository)
        service = PropertySearch(mock_db)
        service.repository = mock_repository

        search_input = SearchRequest(tipoinmueble=["Todos"], polygon=VALID_POLYGON)
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        mock_repository.get_properties_in_polygon.side_effect = Exception(
            "Repository error"
        )

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            service.search_properties(search_input, request_id, timestamp)


# Performance and Edge Case Tests
class TestPerformanceAndEdgeCases:
    """Test performance and edge cases."""

    def test_search_with_large_polygon(self):
        """Test search with large polygon."""
        # Arrange - Large polygon covering significant area
        client = TestClient(app)
        large_polygon = (
            "POLYGON ((-74.1 4.6, -74.0 4.6, -74.0 4.7, -74.1 4.7, -74.1 4.6))"
        )
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": large_polygon,
            "limit": 50,  # Limit results for performance
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_search_with_zero_filters(self):
        """Test search with filters set to zero (edge case)."""
        # Arrange
        client = TestClient(app)
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": VALID_POLYGON,
            "areamin": 0,
            "areamax": 0,
            "estratomin": 0,
            "estratomax": 0,
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_search_with_maximum_limit(self):
        """Test search with maximum allowed limit."""
        # Arrange
        client = TestClient(app)
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": VALID_POLYGON,
            "limit": 1000,  # High limit
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_search_metadata_completeness(self):
        """Test that search metadata is complete and accurate."""
        # Arrange
        client = TestClient(app)
        payload = {
            "tipoinmueble": ["Todos"],
            "polygon": VALID_POLYGON,
            "areamin": 100,
            "areamax": 500,
            "estratomin": 3,
            "estratomax": 6,
            "limit": 10,
            "offset": 5,
        }
        headers = {"Content-Type": "application/json", "x-api-key": VALID_API_KEY}

        # Act
        response = client.post("/api/v1/search/general", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check metadata completeness
        meta = data["meta"]
        assert "timestamp" in meta
        assert "request_id" in meta
        assert "filters_applied" in meta

        # Check filters are correctly captured
        filters = meta["filters_applied"]
        assert "polygon" in filters
        assert "areamin" in filters
        assert filters["areamin"] == 100
        assert "estratomin" in filters
        assert filters["estratomin"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=html"])
