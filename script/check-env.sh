#!/bin/bash

echo "🔍 Environment Variables Check for Urbex API"
echo "============================================"

echo ""
echo "📋 Checking required environment variables:"
echo ""

# Required variables
variables=(
    "DATABASE_URL"
    "SECRET_KEY"
    "AWS_REGION"
)

all_good=true

for var in "${variables[@]}"; do
    if [ -n "${!var}" ]; then
        if [[ "${!var}" == *"your-"* ]]; then
            echo "⚠️  $var: ${!var} (placeholder value)"
            all_good=false
        else
            echo "✅ $var: ${!var}"
        fi
    else
        echo "❌ $var: Not set"
        all_good=false
    fi
done

echo ""
if [ "$all_good" = true ]; then
    echo "🎉 All environment variables are properly configured!"
    echo ""
    echo "🚀 Ready to deploy with: serverless deploy --stage prod"
else
    echo "⚠️  Some variables need to be configured with real values."
    echo ""
    echo "📝 Update your .env file with real values:"
    echo "   - DATABASE_URL: Get from Digital Ocean RDS"
    echo "   - SECRET_KEY: Generate a secure key"
    echo "   - AWS_REGION: Set to us-east-2"
    echo ""
    echo "🔗 Helpful links:"
    echo "   - Digital Ocean RDS: https://cloud.digitalocean.com/databases"
    echo "   - AWS Cognito: https://console.aws.amazon.com/cognito/"
fi
