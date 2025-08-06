# Property Search API

A microservice for searching real estate properties in Bogotá, Colombia based on geographic boundaries and various filters.

## 🚀 Features

- **Geographic Search**: Search properties within WKT polygons
- **Advanced Filtering**: Filter by area, age, socioeconomic stratum, and property use codes
- **Real-time Performance**: Optimized queries with spatial indexing
- **Comprehensive Data**: Full property information including geometry
- **Health Monitoring**: Built-in health check endpoint
- **RESTful API**: Clean, documented REST endpoints
- **Error Handling**: Comprehensive error handling and validation

## 📋 Requirements

- Python 3.9+
- MySQL Aurora AWS database
- FastAPI
- SQLAlchemy
- Pandas

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd real-state
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

4. **Test database connection**
   ```bash
   make test-db
   ```

5. **Run the application**
   ```bash
   make run
   ```

## 🏗️ Architecture

### Project Structure

```
app/
├── api/v1/endpoints/
│   └── search.py              # Search endpoints
├── schemas/
│   └── search.py              # Pydantic schemas
├── services/
│   └── property_search_service.py  # Business logic
├── core/
│   ├── config.py              # Configuration
│   ├── database.py            # Database setup
│   └── logging.py             # Logging configuration
└── models/                    # SQLAlchemy models
    └── bogota_models/         # Bogotá-specific models

tests/
└── test_search.py             # Comprehensive tests

docs/
└── API_SEARCH.md              # API documentation
```

### Design Patterns

- **Service Layer Pattern**: Business logic separated from API layer
- **Repository Pattern**: Database access abstracted through services
- **Dependency Injection**: FastAPI dependency injection for services
- **Factory Pattern**: Service instantiation through dependency injection
- **Strategy Pattern**: Different search strategies for various filters

## 🔧 Configuration

### Environment Variables

```env
# Database Configuration
DB_HOST=your-aurora-endpoint.cluster-xxxxxx.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

# API Configuration
DEBUG=false
LOG_LEVEL=INFO
```

### Database Tables

The API connects to the following MySQL Aurora tables:

- `bigdata.bogota_data_lotes_fastsearch` - Spatial index for fast polygon searches
- `bigdata.bogota_data_caracteristicas` - Property characteristics
- `bigdata.bogota_data_predios` - Property data
- `bigdata.bogota_data_lotes` - Property geometry

## 📚 API Usage

### Basic Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/general" \
  -H "Content-Type: application/json" \
  -d '{
    "polygon": "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))"
  }'
```

### Advanced Search with Filters

```bash
curl -X POST "http://localhost:8000/api/v1/search/general" \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": ["Residential"],
    "min_area": 80.0,
    "max_area": 150.0,
    "min_age": 0,
    "max_age": 15,
    "min_stratum": 4,
    "max_stratum": 6,
    "property_use_codes": ["001", "002"],
    "polygon": "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))"
  }'
```

### Health Check

```bash
curl "http://localhost:8000/api/v1/search/health"
```

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Run Search Tests Only

```bash
make test-search
```

### Run Tests with Coverage

```bash
make test-coverage
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Edge Cases**: Boundary condition testing
- **Error Handling**: Exception and error response testing

## 🔍 Code Quality

### Pre-commit Hooks

The project uses pre-commit hooks to maintain code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Run specific hooks
pre-commit run black
pre-commit run flake8
pre-commit run mypy
```

### Code Quality Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security analysis
- **pytest**: Testing framework

## 📊 Performance

### Query Optimization

- **Spatial Indexing**: Uses MySQL spatial indexes for fast polygon searches
- **Connection Pooling**: SQLAlchemy connection pooling for efficient database connections
- **Query Optimization**: Optimized SQL queries with proper indexing
- **DataFrame Operations**: Efficient pandas operations for data processing

### Performance Metrics

- **Small areas (< 1km²)**: < 500ms response time
- **Medium areas (1-10km²)**: < 2s response time
- **Large areas (> 10km²)**: < 10s response time

### Monitoring

- **Execution Time**: Tracked in response metadata
- **Request ID**: Unique identifier for request tracing
- **Health Checks**: Database connectivity monitoring
- **Error Logging**: Comprehensive error logging with structured logs

## 🚀 Deployment

### Docker Deployment

```bash
# Build Docker image
make docker-build

# Run with Docker Compose
make docker-run

# Stop containers
make docker-stop
```

### Serverless Deployment

```bash
# Deploy to AWS Lambda
make deploy
```

### Production Considerations

- **Environment Variables**: Secure configuration management
- **Database Connection**: Connection pooling and retry logic
- **Logging**: Structured logging for production monitoring
- **Health Checks**: Regular health check endpoints
- **Rate Limiting**: API rate limiting for fair usage
- **Caching**: Redis caching for frequently requested data

## 🔧 Development

### Adding New Filters

1. **Update Schema**: Add new fields to `GeneralSearchInput`
2. **Update Service**: Implement filter logic in `PropertySearchService`
3. **Add Tests**: Create tests for new filter functionality
4. **Update Documentation**: Document new filter in API docs

### Adding New Endpoints

1. **Create Endpoint**: Add new route in `search.py`
2. **Add Service Method**: Implement business logic in service
3. **Add Tests**: Create comprehensive tests
4. **Update Documentation**: Document new endpoint

### Database Changes

1. **Update Models**: Modify SQLAlchemy models if needed
2. **Create Migration**: Use Alembic for database migrations
3. **Update Queries**: Modify service queries if needed
4. **Test Changes**: Verify with integration tests

## 📈 Monitoring and Logging

### Logging Configuration

The application uses structured logging with the following levels:

- **DEBUG**: Detailed debugging information
- **INFO**: General application information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical error messages

### Metrics

- **Request Count**: Number of search requests
- **Response Time**: Average response time
- **Error Rate**: Percentage of failed requests
- **Database Connections**: Active database connections
- **Memory Usage**: Application memory consumption

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make changes**: Follow coding standards and add tests
4. **Run tests**: `make test`
5. **Commit changes**: `git commit -m "Add new feature"`
6. **Push to branch**: `git push origin feature/new-feature`
7. **Create pull request**: Submit for review

### Coding Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Add tests for new functionality
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Documentation**: [API Documentation](docs/API_SEARCH.md)
- **Issues**: Create an issue in the repository
- **Email**: api-support@yourcompany.com

## 🔄 Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- General property search endpoint
- Health check endpoint
- Comprehensive filtering options
- Geographic search with WKT polygons
- Full test coverage
- Production-ready deployment configuration 