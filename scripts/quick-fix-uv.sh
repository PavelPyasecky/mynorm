#!/bin/bash

# Quick fix script to install drf-spectacular using uv
set -e

echo "🚀 Quick fix: Installing drf-spectacular using uv..."

# Install drf-spectacular directly using uv
docker compose -f docker-compose.production.yml exec --user root django bash -c "
    source /venv/bin/activate && \
    uv pip install drf-spectacular==0.27.2 --python /venv/bin/python && \
    chown -R django:django /venv && \
    chmod -R 755 /venv
"

echo "✅ drf-spectacular installed!"

# Restart Django container
docker compose -f docker-compose.production.yml restart django

# Wait and test
sleep 10
echo "🧪 Testing API endpoints..."
curl -I https://dev-314.ru/api/health/ || echo "❌ Health check failed"
curl -I https://dev-314.ru/api/docs/ || echo "❌ Docs endpoint failed"

echo "🎉 Quick fix completed!"
