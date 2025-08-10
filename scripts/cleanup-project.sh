#!/bin/bash

# Script to clean up unnecessary files from the project

set -e

echo "🧹 Project Cleanup Script"
echo "=========================="

# Function to safely remove files/directories
safe_remove() {
    local target=$1
    local description=$2

    if [ -e "$target" ]; then
        echo "🗑️  Removing $description: $target"
        rm -rf "$target"
        echo "   ✅ Removed successfully"
    else
        echo "   ℹ️  $description not found: $target"
    fi
}

echo ""
echo "🚀 Starting cleanup process..."
echo ""

# 1. Remove unnecessary files and directories
echo "📁 Cleaning up build and cache directories..."
safe_remove ".serverless" "Serverless build cache"
safe_remove "__pycache__" "Python cache files"
safe_remove "*.pyc" "Python compiled files"
safe_remove ".pytest_cache" "Pytest cache"
safe_remove "node_modules" "Node modules"
safe_remove ".mypy_cache" "MyPy cache"
safe_remove "htmlcov" "Coverage HTML reports"
safe_remove ".coverage" "Coverage data"

echo ""
echo "📄 Cleaning up temporary and backup files..."
safe_remove "*.log" "Log files"
safe_remove "*.backup" "Backup files"
safe_remove "*.tmp" "Temporary files"
safe_remove "*~" "Editor backup files"
safe_remove ".DS_Store" "MacOS system files"

echo ""
echo "📋 Unnecessary development files to consider removing:"

# Check for files that might be unnecessary but require manual review
echo ""
echo "🔍 Files that might be unnecessary (manual review needed):"

# GitHub workflows (only if not using CI/CD)
if [ -d ".github" ]; then
    echo "   ⚠️  .github/workflows/ - Remove if not using GitHub Actions"
fi

# Pre-commit config (only if not using pre-commit)
if [ -f ".pre-commit-config.yaml" ]; then
    echo "   ⚠️  .pre-commit-config.yaml - Remove if not using pre-commit hooks"
fi

# Package.json and package-lock.json (only if not using Node.js tools)
if [ -f "package.json" ]; then
    echo "   ⚠️  package.json, package-lock.json - Remove if not using Node.js tools"
fi

# Development requirements
echo "   ⚠️  Consider splitting requirements.txt into:"
echo "      - requirements.txt (production)"
echo "      - requirements-dev.txt (development only)"

echo ""
echo "📊 Checking current project size..."

# Calculate project size
PROJECT_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "   📏 Current project size: $PROJECT_SIZE"

# Count files
FILE_COUNT=$(find . -type f | wc -l | xargs)
echo "   📄 Total files: $FILE_COUNT"

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "💡 Manual cleanup recommendations:"
echo "   1. Review and remove unused Python packages from requirements.txt"
echo "   2. Remove unused models in app/models/bogota/ (keep only what's used)"
echo "   3. Clean up any unused scripts in scripts/"
echo "   4. Review and consolidate configuration files"
echo ""
echo "🚀 To apply automatic cleanups, run with --apply flag"

# If --apply flag is provided, actually remove the files
if [ "$1" = "--apply" ]; then
    echo ""
    echo "🗑️  Applying automatic cleanups..."

    # Remove Python cache files recursively
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".DS_Store" -delete 2>/dev/null || true

    echo "   ✅ Automatic cleanup applied!"
fi
