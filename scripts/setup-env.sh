#!/bin/bash

# Environment setup script for real-state-api
set -e

echo "🔧 Setting up environment variables..."

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

# Check if .env file exists
if [ -f ".env" ]; then
    print_status "Loading environment from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    print_warning "No .env file found. Please create one with the following variables:"
    echo ""
    echo "DATABASE_URL=mysql+pymysql://user:password@host:port/database"
    echo "VPC_SECURITY_GROUP_ID=sg-xxxxxxxxx"
    echo "VPC_SUBNET_ID_1=subnet-xxxxxxxxx"
    echo "VPC_SUBNET_ID_2=subnet-xxxxxxxxx"
    echo ""
    print_error "Please set up your environment variables and try again."
    exit 1
fi

# Validate required variables
print_status "Validating environment variables..."

if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL is not set"
    exit 1
fi

if [ -z "$VPC_SECURITY_GROUP_ID" ]; then
    print_warning "VPC_SECURITY_GROUP_ID not set, using default"
    export VPC_SECURITY_GROUP_ID="sg-0123456789abcdef0"
fi

if [ -z "$VPC_SUBNET_ID_1" ]; then
    print_warning "VPC_SUBNET_ID_1 not set, using default"
    export VPC_SUBNET_ID_1="subnet-0123456789abcdef0"
fi

if [ -z "$VPC_SUBNET_ID_2" ]; then
    print_warning "VPC_SUBNET_ID_2 not set, using default"
    export VPC_SUBNET_ID_2="subnet-0123456789abcdef1"
fi

print_success "Environment variables configured successfully!"
print_status "DATABASE_URL: ${DATABASE_URL:0:20}..."
print_status "VPC_SECURITY_GROUP_ID: $VPC_SECURITY_GROUP_ID"
print_status "VPC_SUBNET_ID_1: $VPC_SUBNET_ID_1"
print_status "VPC_SUBNET_ID_2: $VPC_SUBNET_ID_2"
