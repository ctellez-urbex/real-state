#!/bin/bash

# Local deployment script with temporary values
# This script deploys the serverless application with temporary configuration

set -e

echo "🚀 Deploying Real State Search API to AWS Lambda..."

# Check if AWS credentials are configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Set temporary environment variables for deployment
export DATABASE_URL="mysql+pymysql://temp:temp@localhost:3306/temp"
export API_KEYS='["temp-api-key-for-deployment"]'
export ALLOWED_HOSTS='["localhost", "*.execute-api.us-east-2.amazonaws.com"]'
export ALLOWED_ORIGINS='["http://localhost:3000", "https://*.execute-api.us-east-2.amazonaws.com"]'

echo "📋 Using temporary configuration:"
echo "   DATABASE_URL: $DATABASE_URL"
echo "   API_KEYS: $API_KEYS"
echo "   ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "   ALLOWED_ORIGINS: $ALLOWED_ORIGINS"
echo ""

# Deploy to AWS
echo "🔧 Deploying to AWS Lambda..."
serverless deploy --stage prod --verbose

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Get the API Gateway URL from the deployment output above"
echo "2. Go to AWS Console → API Gateway → API Keys"
echo "3. Copy the generated API key"
echo "4. Update GitHub secrets with the real values:"
echo "   - DATABASE_URL: Your actual database URL"
echo "   - API_KEYS: The generated API key"
echo "   - ALLOWED_HOSTS: The API Gateway URL"
echo "   - ALLOWED_ORIGINS: Your frontend URLs"
echo ""
echo "5. Push to developer branch to trigger GitHub Actions deployment"
echo ""
echo "🔗 Your API will be available at:"
echo "   https://{api-id}.execute-api.us-east-2.amazonaws.com/"
echo ""
echo "📚 For detailed configuration, see: scripts/setup-github-secrets.md" 