#!/bin/bash

# Script to install dependencies using poetry in the container
set -e

echo "🔧 Installing dependencies using poetry..."

# Check if container is running
if ! docker compose -f docker-compose.production.yml ps django | grep -q "Up"; then
    echo "❌ Django container is not running. Starting services..."
    docker compose -f docker-compose.production.yml up -d
    sleep 10
fi

echo "📦 Installing dependencies with poetry..."

# Install dependencies using poetry with root privileges
docker compose -f docker-compose.production.yml exec --user root django bash -c "
    source /venv/bin/activate && \
    poetry install --no-dev && \
    chown -R django:django /venv && \
    chmod -R 755 /venv
"

echo "✅ Dependencies installed successfully with poetry!"

# Restart Django container to apply changes
echo "🔄 Restarting Django container..."
docker compose -f docker-compose.production.yml restart django

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Check if Django is working
echo "🔍 Checking Django status..."
docker compose -f docker-compose.production.yml logs django --tail=20

# Test API endpoints
echo "🧪 Testing API endpoints..."
curl -I https://merame.ru/api/health/ || echo "❌ Health check failed"
curl -I https://merame.ru/api/docs/ || echo "❌ Docs endpoint failed"

echo "🎉 Poetry installation completed!"
