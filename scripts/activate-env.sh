#!/bin/bash

# Script to activate the virtual environment and set up the development environment

echo "🔧 Setting up development environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if not already installed
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Development environment ready!"
echo "💡 To activate manually, run: source venv/bin/activate"
echo "🐍 Python version: $(python --version)"
echo "📦 Virtual environment: $VIRTUAL_ENV"
