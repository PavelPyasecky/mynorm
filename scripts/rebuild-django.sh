#!/bin/bash

# Script to rebuild Django container with proper dependency installation
set -e

echo "🔧 Rebuilding Django container with dependencies..."

# Stop containers
echo "⏹️ Stopping containers..."
docker compose -f docker-compose.production.yml down

# Remove old Django image
echo "🗑️ Removing old Django image..."
docker rmi mynorm_production_django 2>/dev/null || true

# Build Django container with verbose output
echo "🔨 Building Django container..."
docker compose -f docker-compose.production.yml build --no-cache --progress=plain django

# Start services
echo "🚀 Starting services..."
docker compose -f docker-compose.production.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check Django logs
echo "📋 Checking Django logs..."
docker compose -f docker-compose.production.yml logs django --tail=20

# Test if drf_spectacular is installed
echo "🧪 Testing drf_spectacular installation..."
docker compose -f docker-compose.production.yml exec django python -c "
try:
    import drf_spectacular
    print('✅ drf_spectacular is installed, version:', drf_spectacular.__version__)
except ImportError as e:
    print('❌ drf_spectacular not found:', e)
"

# Test API endpoints
echo "🌐 Testing API endpoints..."
curl -I https://dev-314.ru/api/health/ || echo "❌ Health check failed"
curl -I https://dev-314.ru/api/docs/ || echo "❌ Docs endpoint failed"

echo "✅ Rebuild completed!"
