#!/bin/bash

# Optimized deployment script for real-state-api
set -e

echo "🚀 Starting optimized deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Load environment variables
print_status "Loading environment variables..."
source ./scripts/setup-env.sh

# Check environment variables
print_status "Checking environment variables..."
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL environment variable is not set"
    exit 1
fi

if [ -z "$VPC_SECURITY_GROUP_ID" ] || [ -z "$VPC_SUBNET_ID_1" ] || [ -z "$VPC_SUBNET_ID_2" ]; then
    print_warning "VPC environment variables not set. Using default values."
fi

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf .serverless/
rm -rf node_modules/.cache/

# Install/update serverless framework
print_status "Checking serverless framework..."
if ! command -v serverless &> /dev/null; then
    print_status "Installing serverless framework..."
    npm install -g serverless
fi

# Deploy with optimization
print_status "Deploying with optimizations..."
serverless deploy --stage prod --verbose

# Check deployment size
print_status "Checking deployment size..."
if [ -f ".serverless/real-state-api.zip" ]; then
    SIZE=$(du -h .serverless/real-state-api.zip | cut -f1)
    print_success "Deployment package size: $SIZE"

    # Check if size is reasonable (should be under 100MB with optimizations)
    SIZE_BYTES=$(du -k .serverless/real-state-api.zip | cut -f1)
    if [ "$SIZE_BYTES" -gt 102400 ]; then  # 100MB in KB
        print_warning "Package size is still large ($SIZE). Consider further optimizations."
    else
        print_success "Package size is within acceptable limits!"
    fi
fi

# Get deployment info
print_status "Getting deployment information..."
serverless info --stage prod

print_success "Deployment completed successfully!"
print_status "API Gateway URL: $(serverless info --stage prod | grep 'endpoints:' -A 1 | tail -n 1 | sed 's/^[[:space:]]*//')"
