#!/bin/bash

echo "🚀 Deploy to Production with Environment Variables"
echo "================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please run the setup scripts first:"
    exit 1
fi

# Load environment variables from .env file
echo "📋 Loading environment variables from .env file..."
export $(cat .env | grep -v '^#' | xargs)

# Verify required variables
echo "🔍 Verifying required environment variables..."

required_vars=(
    "DATABASE_URL"
    "SECRET_KEY"
    "AWS_REGION"
)

missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [[ "${!var}" == *"your-"* ]]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing or invalid environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please update your .env file with real values."
    exit 1
fi

echo "✅ All environment variables are properly configured!"

# Test AWS credentials
echo "🔑 Testing AWS credentials..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials are invalid!"
    echo "Please configure AWS credentials first:"
    echo "  aws configure"
    exit 1
fi

echo "✅ AWS credentials are valid!"

# Deploy to production
echo "🚀 Deploying to production..."
serverless deploy --stage prod

if [ $? -eq 0 ]; then
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "🔗 Your API endpoints:"
    echo "   - API Gateway: Check AWS Console"
    echo "   - Health Check: /health"
    echo "   - Documentation: /docs"
else
    echo "❌ Deployment failed!"
    exit 1
fi
