# Real State Search API - Architecture Documentation

## 🏗️ Clean Architecture Implementation

This document describes the clean architecture implementation of the Real State Search API, highlighting the separation of concerns and design patterns used.

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Controllers)                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    search.py                            │ │
│  │  - /general (POST) - Property search                    │ │
│  │  - /health (GET) - Health check                         │ │
│  │  - /metrics (GET) - Performance metrics                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer (Business Logic)             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              property_search_service.py                 │ │
│  │  - search_properties() - Main search orchestration     │ │
│  │  - _apply_business_filters() - Filter logic            │ │
│  │  - _transform_to_response_format() - Data transform    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Repository Layer (Data Access)               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              property_repository.py                     │ │
│  │  - get_properties_in_polygon()                         │ │
│  │  - get_property_characteristics()                      │ │
│  │  - get_property_data()                                 │ │
│  │  - get_property_geometry()                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            property_use_repository.py                   │ │
│  │  - get_property_use_codes_by_type()                    │ │
│  │  - get_property_use_classification()                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Model Layer (Data Models)                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   SQLAlchemy    │  │    Pydantic     │  │   Database   │ │
│  │     Models      │  │    Schemas      │  │    Tables    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Layer Responsibilities

### 1. API Layer (`app/api/v1/endpoints/`)
**Purpose**: Handle HTTP requests and responses

**Responsibilities**:
- Request validation using Pydantic schemas
- Response formatting
- Error handling and HTTP status codes
- API documentation (OpenAPI/Swagger)

**Key Components**:
- `search.py`: Main search endpoints
- Health check and metrics endpoints
- CORS and middleware configuration

### 2. Service Layer (`app/services/`)
**Purpose**: Implement business logic and orchestrate operations

**Responsibilities**:
- Business rule enforcement
- Data transformation and aggregation
- Filter application logic
- Error handling and logging

**Key Components**:
- `property_search_service.py`: Main search orchestration
- Filter logic for area, age, stratum, and property types
- Response formatting and metadata creation

### 3. Repository Layer (`app/repositories/`)
**Purpose**: Abstract data access and provide clean interfaces

**Responsibilities**:
- Database query execution
- Data mapping and transformation
- Connection management
- Query optimization

**Key Components**:
- `property_repository.py`: Property data access
- `property_use_repository.py`: Property use classification
- Spatial query handling with GeoAlchemy2

### 4. Model Layer (`app/models/` and `app/schemas/`)
**Purpose**: Define data structures and validation rules

**Responsibilities**:
- Database schema mapping (SQLAlchemy)
- API request/response validation (Pydantic)
- Data type definitions

**Key Components**:
- SQLAlchemy models for database tables
- Pydantic schemas for API validation
- Type hints and documentation

## 🔧 Design Patterns Implemented

### 1. Repository Pattern
**Implementation**: `PropertyRepository` and `PropertyUseRepository`

**Benefits**:
- Abstraction of data access logic
- Easy testing with mocks
- Consistent interface for data operations
- Separation of business logic from data access

**Example**:
```python
class PropertyRepository:
    def get_properties_in_polygon(self, polygon: str) -> List[str]:
        """Get barmanpre codes within the specified polygon."""
        
    def get_property_characteristics(self, barmanpre_list: List[str]) -> List[BogotaDataCaracteristicas]:
        """Get property characteristics for the given barmanpre list."""
```

### 2. Dependency Injection
**Implementation**: FastAPI dependency injection system

**Benefits**:
- Loose coupling between components
- Easy testing and mocking
- Configuration management
- Resource lifecycle management

**Example**:
```python
def get_search_service(db: Session = Depends(get_db)) -> PropertySearchService:
    return PropertySearchService(db)
```

### 3. Strategy Pattern (Filter Logic)
**Implementation**: Flexible filtering system

**Benefits**:
- Extensible filter system
- Easy to add new filter types
- Clean separation of filter logic
- Testable individual filters

**Example**:
```python
def _apply_business_filters(self, characteristics: List, search_input: GeneralSearchInput) -> List:
    # Area filters
    # Age filters  
    # Stratum filters
    # Property use filters
```

## 📊 Data Flow

### 1. Search Request Flow
```
Client Request → API Layer → Service Layer → Repository Layer → Database
                ↓
            Validation → Business Logic → Data Access → Response
```

### 2. Filter Application Flow
```
1. Polygon Search → Get barmanpre codes
2. Characteristics → Get property characteristics
3. Business Filters → Apply area, age, stratum, type filters
4. Additional Data → Get property data and geometry
5. Response Format → Transform to API response
```

### 3. Error Handling Flow
```
Exception → Service Layer → API Layer → Client
           ↓
       Logging → Error Response → HTTP Status
```

## 🧪 Testing Strategy

### Test Coverage: 80%

#### Test Categories
1. **Unit Tests**: Individual component testing
   - Repository methods
   - Service business logic
   - Utility functions

2. **Integration Tests**: End-to-end testing
   - API endpoints
   - Database operations
   - Complete workflows

3. **Mock Tests**: Isolated testing
   - External dependencies
   - Database connections
   - Third-party services

#### Test Structure
```
tests/
├── test_search.py
│   ├── TestPropertyRepository
│   ├── TestPropertyUseRepository
│   ├── TestPropertySearchService
│   └── TestSearchEndpoints
```

## 🔒 Security Considerations

### 1. Input Validation
- Pydantic schema validation
- Polygon format validation
- SQL injection prevention
- Parameter sanitization

### 2. Authentication & Authorization
- API key validation
- CORS configuration
- Rate limiting (future)
- Request logging

### 3. Data Protection
- Sensitive data encryption
- Secure database connections
- Environment variable management
- Secrets management (AWS Secrets Manager)

## 📈 Performance Optimizations

### 1. Database Optimization
- Spatial indexes for polygon queries
- Efficient IN clause handling
- Connection pooling
- Query optimization

### 2. Application Optimization
- Conditional data fetching
- Response caching (future)
- Async operations (future)
- Memory management

### 3. Monitoring & Metrics
- Execution time tracking
- Request/response logging
- Performance metrics endpoint
- Health check monitoring

## 🚀 Deployment Architecture

### CI/CD Pipeline
```
GitHub Push → GitHub Actions → Tests → Build → ECR → ECS → Production
```

### Infrastructure
- **Container Registry**: Amazon ECR
- **Orchestration**: Amazon ECS Fargate
- **Secrets**: AWS Secrets Manager
- **Logging**: AWS CloudWatch
- **Monitoring**: Health checks and metrics

## 🔄 Future Enhancements

### 1. Performance Improvements
- Redis caching layer
- Async/await implementation
- Database connection pooling
- Query result caching

### 2. Feature Additions
- Advanced search filters
- Geospatial analytics
- Export functionality
- Batch operations

### 3. Scalability
- Load balancing
- Auto-scaling
- Microservices architecture
- Event-driven architecture

## 📚 Best Practices Followed

### 1. Code Quality
- Type hints throughout
- Comprehensive documentation
- PEP 8 compliance
- Clean code principles

### 2. Testing
- High test coverage (80%)
- Unit and integration tests
- Mock testing
- Test-driven development

### 3. Security
- Input validation
- Secure configuration
- Error handling
- Logging and monitoring

### 4. Performance
- Efficient queries
- Optimized data structures
- Resource management
- Monitoring and metrics

## 📞 Support & Maintenance

### Documentation
- API documentation (OpenAPI)
- Architecture documentation
- Deployment guide
- Troubleshooting guide

### Monitoring
- Application logs
- Performance metrics
- Error tracking
- Health monitoring

### Maintenance
- Regular dependency updates
- Security patches
- Performance optimization
- Feature enhancements 