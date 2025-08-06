# Property Search API Documentation

## Overview

The Property Search API provides comprehensive search functionality for real estate properties in Bogotá, Colombia. This microservice allows users to search for properties based on geographic boundaries, property characteristics, and various filters.

## Base URL

```
https://your-api-domain.com/api/v1/search
```

## Authentication

The API uses Bearer token authentication. Include your token in the Authorization header:

```
Authorization: Bearer your-token-here
```

## Endpoints

### 1. General Property Search

**POST** `/general`

Search for properties within a specified geographic polygon with various filters.

#### Request Body

```json
{
  "property_type": ["Residential", "Commercial"],
  "min_area": 50.0,
  "max_area": 200.0,
  "min_age": 0,
  "max_age": 20,
  "min_stratum": 3,
  "max_stratum": 5,
  "property_use_codes": ["001", "002"],
  "polygon": "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))"
}
```

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `property_type` | Array[string] | No | List of property types to filter by | `["Residential", "Commercial"]` |
| `min_area` | float | No | Minimum built area in square meters | `50.0` |
| `max_area` | float | No | Maximum built area in square meters | `200.0` |
| `min_age` | integer | No | Minimum property age in years | `0` |
| `max_age` | integer | No | Maximum property age in years | `20` |
| `min_stratum` | integer | No | Minimum socioeconomic stratum (0-6) | `3` |
| `max_stratum` | integer | No | Maximum socioeconomic stratum (0-6) | `5` |
| `property_use_codes` | Array[string] | No | List of property use codes to filter by | `["001", "002"]` |
| `polygon` | string | **Yes** | WKT polygon for geographic search | `"POLYGON ((...))"` |

#### Response

**Success (200 OK)**

```json
{
  "meta": {
    "timestamp": "2024-01-15T10:30:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "total_results": 150,
    "filters_applied": {
      "property_type": ["Residential"],
      "min_area": 50.0,
      "max_area": 200.0,
      "min_age": 0,
      "max_age": 20,
      "min_stratum": 3,
      "max_stratum": 5,
      "property_use_codes": ["001", "002"],
      "polygon": "POLYGON ((-74.052315 4.690699, ...))"
    },
    "execution_time_ms": 245.67
  },
  "data": [
    {
      "barmanpre": "1100100000000000001",
      "preaconst": 120.5,
      "preaterre": 150.0,
      "prevetustz": 15,
      "precuso": "001",
      "precdestin": "70",
      "estrato": 4,
      "predios": "Property information",
      "connpisos": "Floor information",
      "connsotano": "Basement information",
      "contsemis": "Semi-basement information",
      "conelevaci": "Elevation information",
      "formato_direccion": "Calle 123 # 45-67",
      "nombre_conjunto": "Building Complex Name",
      "prenbarrio": "Chapinero",
      "precbarrio": "11001",
      "locnombre": "Chapinero",
      "preusoph": "Residential",
      "manzcodigo": "1100100001",
      "wkt": "POINT (-74.052315 4.690699)"
    }
  ]
}
```

**Error Responses**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 400 | Bad Request - Invalid input parameters | `{"detail": "Polygon is required"}` |
| 422 | Validation Error | `{"detail": [{"loc": ["body", "polygon"], "msg": "Polygon must be in WKT POLYGON format", "type": "value_error"}]}` |
| 500 | Internal Server Error | `{"detail": "An unexpected error occurred during the search"}` |

### 2. Health Check

**GET** `/health`

Check the health status of the search service and database connection.

#### Response

**Success (200 OK)**

```json
{
  "status": "healthy",
  "service": "property_search",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error (503 Service Unavailable)**

```json
{
  "status": "unhealthy",
  "service": "property_search",
  "database": "disconnected",
  "error": "Database connection failed",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Data Models

### PropertyResult

| Field | Type | Description |
|-------|------|-------------|
| `barmanpre` | string | Barmanpre property identifier |
| `preaconst` | float | Built area in square meters |
| `preaterre` | float | Land area in square meters |
| `prevetustz` | integer | Property age in years |
| `precuso` | string | Property use code |
| `precdestin` | string | Property destination code |
| `estrato` | integer | Socioeconomic stratum |
| `predios` | string | Property information |
| `connpisos` | string | Floor information |
| `connsotano` | string | Basement information |
| `contsemis` | string | Semi-basement information |
| `conelevaci` | string | Elevation information |
| `formato_direccion` | string | Formatted address |
| `nombre_conjunto` | string | Building complex name |
| `prenbarrio` | string | Neighborhood name |
| `precbarrio` | string | Neighborhood code |
| `locnombre` | string | District name |
| `preusoph` | string | Property use |
| `manzcodigo` | string | Block code |
| `wkt` | string | WKT geometry representation |

### SearchMeta

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | Search execution timestamp |
| `request_id` | string | Unique request identifier |
| `total_results` | integer | Total number of results found |
| `filters_applied` | object | Filters applied to the search |
| `execution_time_ms` | float | Search execution time in milliseconds |

## Usage Examples

### Example 1: Basic Search

Search for all properties within a specific area:

```bash
curl -X POST "https://your-api-domain.com/api/v1/search/general" \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "polygon": "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))"
  }'
```

### Example 2: Filtered Search

Search for residential properties with specific criteria:

```bash
curl -X POST "https://your-api-domain.com/api/v1/search/general" \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": ["Residential"],
    "min_area": 80.0,
    "max_area": 150.0,
    "min_age": 0,
    "max_age": 15,
    "min_stratum": 4,
    "max_stratum": 6,
    "polygon": "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))"
  }'
```

### Example 3: Commercial Properties

Search for commercial properties with specific use codes:

```bash
curl -X POST "https://your-api-domain.com/api/v1/search/general" \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": ["Commercial"],
    "property_use_codes": ["001", "002", "003"],
    "min_area": 100.0,
    "polygon": "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))"
  }'
```

## Polygon Format

The API uses Well-Known Text (WKT) format for geographic polygons. The polygon must be a valid WKT POLYGON string with coordinates in decimal degrees (longitude, latitude).

### Valid Polygon Examples

```wkt
# Simple rectangle
POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))

# Complex polygon
POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))
```

### Invalid Polygon Examples

```wkt
# Missing POLYGON keyword
(0 0, 1 0, 1 1, 0 1, 0 0)

# Invalid coordinate format
POLYGON ((0, 0, 1, 0, 1, 1, 0, 1, 0, 0))

# Not closed polygon
POLYGON ((0 0, 1 0, 1 1))
```

## Error Handling

The API provides detailed error messages to help debug issues:

### Common Errors

1. **Invalid Polygon Format**
   ```json
   {
     "detail": "Polygon must be in WKT POLYGON format"
   }
   ```

2. **Missing Required Field**
   ```json
   {
     "detail": "Polygon is required"
   }
   ```

3. **Invalid Range Values**
   ```json
   {
     "detail": "max_area must be greater than min_area"
   }
   ```

4. **Database Connection Error**
   ```json
   {
     "detail": "An unexpected error occurred during the search"
   }
   ```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Rate Limit**: 100 requests per minute per API key
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information is included in response headers

## Performance Considerations

### Query Optimization

- Use smaller polygons for faster searches
- Limit the number of property types and use codes
- Consider pagination for large result sets

### Response Times

- **Small areas (< 1km²)**: < 500ms
- **Medium areas (1-10km²)**: < 2s
- **Large areas (> 10km²)**: < 10s

### Best Practices

1. **Cache Results**: Cache search results for frequently requested areas
2. **Batch Requests**: Combine multiple searches when possible
3. **Monitor Performance**: Use the `execution_time_ms` field to monitor query performance
4. **Error Handling**: Implement proper error handling for network issues

## SDK Examples

### Python

```python
import requests

def search_properties(polygon, filters=None):
    url = "https://your-api-domain.com/api/v1/search/general"
    headers = {
        "Authorization": "Bearer your-token-here",
        "Content-Type": "application/json"
    }
    
    data = {
        "polygon": polygon,
        **(filters or {})
    }
    
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Usage
results = search_properties(
    polygon="POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))",
    filters={
        "property_type": ["Residential"],
        "min_area": 80.0,
        "max_area": 150.0
    }
)
```

### JavaScript

```javascript
async function searchProperties(polygon, filters = {}) {
    const url = 'https://your-api-domain.com/api/v1/search/general';
    const headers = {
        'Authorization': 'Bearer your-token-here',
        'Content-Type': 'application/json'
    };
    
    const data = {
        polygon,
        ...filters
    };
    
    const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Usage
const results = await searchProperties(
    "POLYGON ((-74.052315 4.690699, -74.052422 4.689929, -74.051349 4.689779, -74.051285 4.690399, -74.052315 4.690699))",
    {
        property_type: ["Residential"],
        min_area: 80.0,
        max_area: 150.0
    }
);
```

## Support

For technical support or questions about the API:

- **Documentation**: [API Documentation](https://your-api-domain.com/docs)
- **Email**: api-support@yourcompany.com
- **Status Page**: [API Status](https://status.yourcompany.com)

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- General property search endpoint
- Health check endpoint
- Comprehensive filtering options
- Geographic search with WKT polygons 