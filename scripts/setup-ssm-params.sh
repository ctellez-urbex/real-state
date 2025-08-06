#!/bin/bash

# Setup SSM Parameters for Real State Search API
# This script creates the necessary SSM parameters for serverless deployment

set -e

# Configuration
STAGE=${1:-dev}
REGION="us-east-2"
SERVICE_NAME="real-state-search-api"

echo "Setting up SSM parameters for $SERVICE_NAME in stage: $STAGE"

# Function to create SSM parameter
create_ssm_param() {
    local param_name=$1
    local param_value=$2
    local param_type=${3:-String}
    
    echo "Creating parameter: $param_name"
    
    aws ssm put-parameter \
        --name "$param_name" \
        --value "$param_value" \
        --type "$param_type" \
        --region "$REGION" \
        --overwrite
}

# Database URL parameter
echo "Enter your database URL (mysql+pymysql://user:password@host:port/database):"
read -r DATABASE_URL

create_ssm_param "/real-state/$STAGE/database-url" "$DATABASE_URL" "SecureString"

# API Keys parameter
echo "Enter your API keys as JSON array (e.g., [\"key1\", \"key2\"]):"
read -r API_KEYS

create_ssm_param "/real-state/$STAGE/api-keys" "$API_KEYS" "SecureString"

# Allowed Hosts parameter
echo "Enter allowed hosts as JSON array (e.g., [\"your-domain.com\"]):"
read -r ALLOWED_HOSTS

create_ssm_param "/real-state/$STAGE/allowed-hosts" "$ALLOWED_HOSTS" "String"

# Allowed Origins parameter
echo "Enter allowed origins as JSON array (e.g., [\"https://your-frontend.com\"]):"
read -r ALLOWED_ORIGINS

create_ssm_param "/real-state/$STAGE/allowed-origins" "$ALLOWED_ORIGINS" "String"

echo "✅ SSM parameters created successfully!"
echo ""
echo "Parameters created:"
echo "- /real-state/$STAGE/database-url"
echo "- /real-state/$STAGE/api-keys"
echo "- /real-state/$STAGE/allowed-hosts"
echo "- /real-state/$STAGE/allowed-origins"
echo ""
echo "You can now deploy with:"
echo "serverless deploy --stage $STAGE" 