#!/bin/bash

# Script to update requirements.txt from pyproject.toml
set -e

echo "🔄 Updating requirements.txt from pyproject.toml..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Installing poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Export requirements from pyproject.toml
echo "📦 Exporting requirements from pyproject.toml..."
poetry export -f requirements.txt --output requirements.txt --without-hashes

echo "✅ requirements.txt updated successfully!"

# Show the updated requirements
echo "📋 Updated requirements:"
head -20 requirements.txt
