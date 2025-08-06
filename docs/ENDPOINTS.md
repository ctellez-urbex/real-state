# API Endpoints Documentation

This document describes all the endpoints exposed by the Real State Search API in the serverless deployment.

## 🚀 **Base URL**

After deployment, your API will be available at:
```
https://{api-id}.execute-api.us-east-2.amazonaws.com/
```

## 📋 **Available Endpoints**

### 🔐 **Protected Endpoints (Require Bearer Token)**

#### **1. Property Search**
```http
POST /api/v1/search/general
```

**Description**: Main property search endpoint with advanced filtering capabilities.

**Headers**:
```
Authorization: Bearer your-api-key
Content-Type: application/json
```

**Request Body**:
```json
{
  "polygon": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
  "property_type": ["residencial"],
  "min_area": 50,
  "max_area": 200,
  "min_age": 0,
  "max_age": 20,
  "min_stratum": 3,
  "max_stratum": 5,
  "property_use_codes": []
}
```

**Response**:
```json
{
  "data": [
    {
      "barmanpre": "123456789",
      "area": 150.5,
      "stratum": 4,
      "age": 10,
      "property_type": "residencial",
      "geometry": "POINT (-74.123 4.567)"
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "per_page": 100,
    "execution_time": 0.5
  }
}
```

#### **2. API Root**
```http
GET /
```

**Description**: Root endpoint with API information.

**Headers**:
```
Authorization: Bearer your-api-key
```

**Response**:
```json
{
  "app_name": "Real Estate API",
  "version": "1.0.0",
  "environment": "prod",
  "status": "active",
  "timestamp": 1628196600.0
}
```

#### **3. API Documentation**
```http
GET /docs
```

**Description**: Interactive API documentation (Swagger UI).

**Headers**:
```
Authorization: Bearer your-api-key
```

**Response**: HTML page with interactive API documentation.

### 🔓 **Public Endpoints (No Authentication Required)**

#### **4. Health Check**
```http
GET /health
```

**Description**: Health check endpoint to verify service status.

**Headers**: None required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T00:00:00.000000",
  "service": "real-state-search-api",
  "environment": "serverless",
  "region": "us-east-2"
}
```

## 🔐 **Authentication**

### Bearer Token Authentication

All protected endpoints require a valid Bearer token in the Authorization header:

```http
Authorization: Bearer your-api-key
```

### API Key Management

API keys are managed through AWS SSM Parameter Store:
- **Parameter**: `/real-state/{stage}/api-keys`
- **Format**: JSON array of strings
- **Example**: `["key1", "key2", "key3"]`

## 📊 **Usage Examples**

### **cURL Examples**

#### **1. Property Search**
```bash
curl -X POST "https://{api-id}.execute-api.us-east-2.amazonaws.com/api/v1/search/general" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "polygon": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
    "property_type": ["residencial"],
    "min_area": 50,
    "max_area": 200
  }'
```

#### **2. Health Check**
```bash
curl -X GET "https://{api-id}.execute-api.us-east-2.amazonaws.com/health"
```

#### **3. API Information**
```bash
curl -X GET "https://{api-id}.execute-api.us-east-2.amazonaws.com/" \
  -H "Authorization: Bearer your-api-key"
```

### **JavaScript/Node.js Examples**

#### **1. Property Search**
```javascript
const response = await fetch('https://{api-id}.execute-api.us-east-2.amazonaws.com/api/v1/search/general', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    polygon: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))',
    property_type: ['residencial'],
    min_area: 50,
    max_area: 200
  })
});

const data = await response.json();
console.log(data);
```

#### **2. Health Check**
```javascript
const response = await fetch('https://{api-id}.execute-api.us-east-2.amazonaws.com/health');
const data = await response.json();
console.log(data);
```

## 🚨 **Error Responses**

### **401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

### **403 Forbidden**
```json
{
  "detail": "Invalid API key"
}
```

### **422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "polygon"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### **500 Internal Server Error**
```json
{
  "detail": "An error occurred during the search"
}
```

## 📈 **Rate Limiting**

- **Rate Limit**: 1000 requests/second
- **Burst Limit**: 2000 requests
- **Monthly Quota**: 100,000 requests

## 🔧 **Testing Endpoints**

### **Local Testing**
```bash
# Test locally before deployment
make local

# Test with curl
curl -X POST "http://localhost:8000/api/v1/search/general" \
  -H "Content-Type: application/json" \
  -d '{"polygon": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"}'
```

### **Serverless Testing**
```bash
# Test serverless function locally
make invoke

# Deploy and test
make deploy-dev
curl -X POST "https://{api-id}.execute-api.us-east-2.amazonaws.com/api/v1/search/general" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"polygon": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"}'
```

## 📝 **Notes**

1. **Cold Starts**: First request may take 1-3 seconds due to Lambda cold start
2. **Timeout**: Requests timeout after 30 seconds
3. **CORS**: All endpoints support CORS for web applications
4. **Logging**: All requests are logged to CloudWatch
5. **Monitoring**: Use CloudWatch for performance monitoring 