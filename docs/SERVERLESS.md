# Serverless Deployment Guide

This document provides comprehensive instructions for deploying the Real State Search API using AWS Serverless Framework with API Gateway integration.

## 🚀 Overview

The serverless deployment uses:
- **AWS Lambda** for compute
- **API Gateway v2** for HTTP API
- **AWS SSM Parameter Store** for configuration
- **Bearer Token Authentication** for API security
- **Mangum** for FastAPI to Lambda integration

## 📋 Prerequisites

### Required Tools
```bash
# Install Node.js and npm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install node

# Install Serverless Framework
npm install -g serverless

# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

### AWS Permissions
Your AWS user/role needs these permissions:
- Lambda: Create, update, delete functions
- API Gateway: Create, update, delete APIs
- IAM: Create roles and policies
- SSM: Create and read parameters
- CloudWatch: Create log groups
- Secrets Manager: Read secrets (if using)

## 🛠️ Configuration

### 1. Setup SSM Parameters
Run the setup script to configure parameters:

```bash
make setup-ssm
```

This will create:
- `/real-state/{stage}/database-url` - Database connection string
- `/real-state/{stage}/api-keys` - Valid API keys for Bearer authentication
- `/real-state/{stage}/allowed-hosts` - Allowed host domains
- `/real-state/{stage}/allowed-origins` - CORS allowed origins

### 2. Manual SSM Setup
Alternatively, create parameters manually:

```bash
# Database URL
aws ssm put-parameter \
  --name "/real-state/dev/database-url" \
  --value "mysql+pymysql://user:password@host:port/database" \
  --type "SecureString" \
  --region us-east-2

# API Keys
aws ssm put-parameter \
  --name "/real-state/dev/api-keys" \
  --value '["your-api-key-1", "your-api-key-2"]' \
  --type "SecureString" \
  --region us-east-2

# Allowed Hosts
aws ssm put-parameter \
  --name "/real-state/dev/allowed-hosts" \
  --value '["your-domain.com"]' \
  --type "String" \
  --region us-east-2

# Allowed Origins
aws ssm put-parameter \
  --name "/real-state/dev/allowed-origins" \
  --value '["https://your-frontend.com"]' \
  --type "String" \
  --region us-east-2
```

## 🚀 Deployment

### Development Deployment
```bash
# Deploy to development stage
make deploy-dev

# Or directly with serverless
serverless deploy --stage dev --verbose
```

### Production Deployment
```bash
# Deploy to production stage
make deploy-prod

# Or directly with serverless
serverless deploy --stage prod --verbose
```

### Deployment Output
After successful deployment, you'll see:
```
endpoints:
  ANY - https://{api-id}.execute-api.us-east-2.amazonaws.com/{proxy+}
  GET - https://{api-id}.execute-api.us-east-2.amazonaws.com/health
```

## 🔐 Authentication

### Bearer Token Authentication
The API uses Bearer token authentication:

```bash
# Example request
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

### API Key Management
- API keys are stored in SSM Parameter Store
- Keys are validated by the Lambda authorizer
- Invalid or missing tokens return 401 Unauthorized

## 📊 Monitoring

### CloudWatch Logs
```bash
# View logs
make logs

# Or directly
serverless logs --stage dev --tail
```

### Lambda Metrics
Monitor in AWS Console:
- Invocation count
- Error rate
- Duration
- Throttles

### API Gateway Metrics
Monitor in AWS Console:
- Request count
- 4xx/5xx errors
- Latency
- Cache hit rate

## 🔧 Configuration Files

### serverless.yml
Main configuration file with:
- Lambda function definitions
- API Gateway configuration
- IAM roles and permissions
- Environment variables
- Usage plans and throttling

### wsgi_handler.py
WSGI handler for FastAPI integration:
- Mangum adapter for Lambda
- CORS headers
- Request/response processing

### app/api/v1/endpoints/health.py
Health check endpoint:
- Lambda-specific handler
- No authentication required
- Basic health status

## 🚨 Troubleshooting

### Common Issues

#### 1. Deployment Fails
```bash
# Check serverless logs
serverless deploy --stage dev --verbose

# Verify AWS credentials
aws sts get-caller-identity

# Check SSM parameters exist
aws ssm get-parameter --name "/real-state/dev/database-url" --region us-east-2
```

#### 2. API Returns 401
- Verify API key is correct
- Check SSM parameter format (JSON array)
- Ensure authorizer function is working

#### 3. Database Connection Fails
- Verify DATABASE_URL parameter
- Check VPC configuration (if using RDS)
- Ensure Lambda has network access

#### 4. CORS Issues
- Verify ALLOWED_ORIGINS parameter
- Check preflight request handling
- Ensure headers are properly set

### Debug Commands
```bash
# Test function locally
make invoke

# Package without deploying
make package

# Get deployment info
make info

# Remove deployment
make remove
```

## 📈 Performance

### Lambda Configuration
- **Memory**: 512 MB (configurable)
- **Timeout**: 30 seconds
- **Concurrency**: 10 reserved (configurable)

### API Gateway Configuration
- **Rate Limit**: 1000 requests/second
- **Burst Limit**: 2000 requests
- **Quota**: 100,000 requests/month

### Optimization Tips
1. **Cold Start**: Use provisioned concurrency for production
2. **Memory**: Increase memory for better CPU performance
3. **Dependencies**: Use Lambda layers for large dependencies
4. **Connection Pooling**: Implement for database connections

## 🔒 Security

### Network Security
- Lambda functions run in VPC (if configured)
- API Gateway provides HTTPS endpoints
- No direct internet access to Lambda

### Data Security
- SSM parameters are encrypted
- API keys are stored securely
- Database connections use SSL

### Access Control
- IAM roles with minimal permissions
- API Gateway usage plans
- Bearer token authentication

## 🔄 CI/CD Integration

### GitHub Actions
The existing workflow can be extended for serverless:

```yaml
- name: Deploy to Serverless
  run: |
    npm install -g serverless
    serverless deploy --stage ${{ github.ref_name }}
```

### Environment Promotion
```bash
# Promote from dev to prod
serverless deploy --stage prod --verbose
```

## 📚 Resources

- [Serverless Framework Documentation](https://www.serverless.com/framework/docs/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Mangum Documentation](https://mangum.io/)

## 🤝 Support

For serverless deployment issues:
1. Check CloudWatch logs first
2. Verify SSM parameters
3. Test function locally
4. Review IAM permissions
5. Contact the DevOps team 