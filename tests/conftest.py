"""
Pytest configuration and fixtures.

This module contains pytest configuration and common fixtures
used across all tests.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: Test client instance
    """
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """
    Create an async test client for the FastAPI application.

    Returns:
        AsyncClient: Async test client instance
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_user() -> dict:
    """
    Create a mock user for testing.

    Returns:
        dict: Mock user data
    """
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
    }


@pytest.fixture
def mock_property() -> dict:
    """
    Create a mock property for testing.

    Returns:
        dict: Mock property data
    """
    return {
        "id": 1,
        "title": "Test Property",
        "description": "A test property for testing purposes",
        "price": 200000.0,
        "property_type": "house",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 150.0,
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "is_available": True,
        "owner_id": 1,
    }
