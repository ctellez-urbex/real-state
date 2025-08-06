#!/bin/bash

# Real Estate API - Serverless Deployment Script
# This script handles the deployment of the API to AWS Lambda using Serverless Framework

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
STAGE=${1:-dev}
REGION=${2:-us-east-1}
REMOVE=${3:-false}

echo -e "${BLUE}🚀 Real Estate API - Serverless Deployment${NC}"
echo -e "${BLUE}==========================================${NC}"
echo -e "Stage: ${GREEN}$STAGE${NC}"
echo -e "Region: ${GREEN}$REGION${NC}"
echo -e "Remove: ${GREEN}$REMOVE${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Serverless Framework is installed
if ! command -v serverless &> /dev/null; then
    echo -e "${YELLOW}⚠️  Serverless Framework is not installed. Installing...${NC}"
    npm install -g serverless
fi

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Installing Node.js dependencies...${NC}"
    npm install
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating Python virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Set up AWS credentials if not configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${YELLOW}⚠️  AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Create SSM parameters for the stage if they don't exist
echo -e "${BLUE}🔧 Setting up SSM parameters for stage: $STAGE${NC}"

# Function to create SSM parameter if it doesn't exist
create_ssm_parameter() {
    local param_name=$1
    local param_value=$2
    local param_type=${3:-String}
    
    if ! aws ssm get-parameter --name "$param_name" --region "$REGION" &> /dev/null; then
        echo -e "${YELLOW}Creating SSM parameter: $param_name${NC}"
        aws ssm put-parameter \
            --name "$param_name" \
            --value "$param_value" \
            --type "$param_type" \
            --region "$REGION" \
            --overwrite
    else
        echo -e "${GREEN}SSM parameter already exists: $param_name${NC}"
    fi
}

# Create SSM parameters
create_ssm_parameter "/real-estate-api/$STAGE/secret-key" "your-super-secret-key-change-in-production-$STAGE"
create_ssm_parameter "/real-estate-api/$STAGE/allowed-hosts" "https://your-domain.com,https://api.your-domain.com"
create_ssm_parameter "/real-estate-api/$STAGE/database-url" "postgresql://user:password@your-rds-endpoint:5432/real_estate_db"

echo ""

# Remove existing deployment if requested
if [ "$REMOVE" = "true" ]; then
    echo -e "${YELLOW}🗑️  Removing existing deployment...${NC}"
    serverless remove --stage "$STAGE" --region "$REGION"
    echo -e "${GREEN}✅ Deployment removed successfully${NC}"
    exit 0
fi

# Deploy the application
echo -e "${BLUE}🚀 Deploying to AWS Lambda...${NC}"
serverless deploy --stage "$STAGE" --region "$REGION"

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Information:${NC}"
serverless info --stage "$STAGE" --region "$REGION"

echo ""
echo -e "${BLUE}🔗 API Endpoints:${NC}"
echo -e "API Gateway URL: ${GREEN}$(serverless info --stage "$STAGE" --region "$REGION" --verbose | grep -o 'https://[^ ]*')${NC}"
echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "View logs: ${YELLOW}serverless logs -f api --stage $STAGE --region $REGION${NC}"
echo -e "Remove deployment: ${YELLOW}./scripts/deploy-serverless.sh $STAGE $REGION true${NC}"
echo -e "Package without deploying: ${YELLOW}serverless package --stage $STAGE --region $REGION${NC}"

# Deactivate virtual environment
deactivate

echo ""
echo -e "${GREEN}🎉 Deployment script completed!${NC}" 