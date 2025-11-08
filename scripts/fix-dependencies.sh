#!/bin/bash

# Script to fix dependency installation issues
set -e

echo "🔧 Fixing Django dependencies..."

# Stop containers
echo "📦 Stopping containers..."
docker compose -f docker-compose.production.yml down

# Remove old images to force rebuild
echo "🗑️ Removing old images..."
docker rmi mynorm_production_django 2>/dev/null || true

# Rebuild Django container
echo "🔨 Rebuilding Django container..."
docker compose -f docker-compose.production.yml build --no-cache django

# Start services
echo "🚀 Starting services..."
docker compose -f docker-compose.production.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if Django is working
echo "🔍 Checking Django status..."
docker compose -f docker-compose.production.yml logs django

# Test API endpoints
echo "🧪 Testing API endpoints..."
curl -I https://merame.ru/api/health/ || echo "❌ Health check failed"
curl -I https://merame.ru/api/docs/ || echo "❌ Docs endpoint failed"

echo "✅ Dependency fix completed!"
