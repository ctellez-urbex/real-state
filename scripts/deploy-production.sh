#!/bin/bash

# Production deployment script for real-state-api
set -e

echo "🚀 Deploying to production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "serverless.yml" ]; then
    print_error "serverless.yml not found. Please run this script from the project root."
    exit 1
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Run ./scripts/activate-env.sh first."
    exit 1
fi

source venv/bin/activate

# Load environment variables
if [ ! -f ".env" ]; then
    print_error ".env file not found. Please create it from env.example."
    exit 1
fi

export $(cat .env | xargs)

# Verify required environment variables
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL not set in .env file."
    exit 1
fi

if [ -z "$VPC_SECURITY_GROUP_ID" ]; then
    print_error "VPC_SECURITY_GROUP_ID not set in .env file."
    exit 1
fi

print_status "Environment variables loaded successfully."

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf .serverless/
rm -rf .requirements/

# Deploy to production
print_status "Deploying to production..."
serverless deploy --stage prod --verbose

print_success "Deployment completed successfully!"

# Get deployment info
print_status "Getting deployment information..."
serverless info --stage prod

print_success "Production deployment ready!"
print_status "API Endpoint: https://2inmopwwug.execute-api.us-east-2.amazonaws.com/prod"
print_status "API Key: n2AZJrlRXF8o45FjuYiEk4T5g9kdDxTv4OSxtJDC"
