#!/bin/bash

# Script to run Pylint on the project
set -e

echo "🔍 Running Pylint on the project..."

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

# Activate virtual environment
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Run ./scripts/activate-env.sh first."
    exit 1
fi

source venv/bin/activate

# Check if Pylint is installed
if ! python -c "import pylint" 2>/dev/null; then
    print_status "Installing Pylint..."
    pip install pylint
fi

# Run Pylint on the app directory
print_status "Running Pylint on app/ directory..."
python -m pylint app/ --rcfile=.pylintrc --ignore=app/models/bogota/ || true

print_success "Pylint analysis completed!"
print_status "Note: Some warnings are expected for SQLAlchemy patterns and development code."
