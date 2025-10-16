#!/bin/bash

# Script to debug and fix Docker build issues
set -e

echo "🔍 Debugging Docker build issues..."

# Check if poetry.lock exists
if [ ! -f "poetry.lock" ]; then
    echo "❌ poetry.lock not found. Generating it..."
    poetry lock
fi

# Check if requirements.txt exists and is up to date
if [ ! -f "requirements.txt" ] || [ "requirements.txt" -ot "pyproject.toml" ]; then
    echo "📦 Updating requirements.txt from pyproject.toml..."
    poetry export -f requirements.txt --output requirements.txt --without-hashes
fi

# Show requirements.txt content
echo "📋 Current requirements.txt:"
head -10 requirements.txt

# Try building with more verbose output
echo "🔨 Building Django container with verbose output..."
docker compose -f docker-compose.production.yml build --no-cache --progress=plain django

echo "✅ Build completed!"
