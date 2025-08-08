#!/bin/bash

# Manual packaging script for real-state-api
set -e

echo "📦 Starting manual packaging..."

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

# Create temporary directory
TEMP_DIR=$(mktemp -d)
print_status "Created temporary directory: $TEMP_DIR"

# Copy application files
print_status "Copying application files..."
cp -r app/ "$TEMP_DIR/"
cp -r requirements.txt "$TEMP_DIR/"

# Install dependencies in temporary directory
print_status "Installing dependencies..."
cd "$TEMP_DIR"
pip install -r requirements.txt -t .

# Remove unnecessary files
print_status "Cleaning up unnecessary files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Create zip file
print_status "Creating deployment package..."
cd /Users/ctellez/developer/back/real-state
cd "$TEMP_DIR"
zip -r /Users/ctellez/developer/back/real-state/.serverless/real-state-api-manual.zip ./*
cd /Users/ctellez/developer/back/real-state

# Clean up
rm -rf "$TEMP_DIR"

# Check size
SIZE=$(du -h .serverless/real-state-api-manual.zip | cut -f1)
print_success "Package created successfully! Size: $SIZE"

print_status "Package location: .serverless/real-state-api-manual.zip"
