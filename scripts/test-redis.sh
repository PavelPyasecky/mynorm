#!/bin/bash

# Script to test Redis connectivity
set -e

echo "🔍 Testing Redis connectivity..."

# Check if Redis container is running
if ! docker compose -f docker-compose.production.yml ps redis | grep -q "Up"; then
    echo "❌ Redis container is not running. Starting services..."
    docker compose -f docker-compose.production.yml up -d redis
    sleep 5
fi

# Test Redis connection
echo "📡 Testing Redis connection..."
docker compose -f docker-compose.production.yml exec redis redis-cli ping

# Test Redis from Django container
echo "🐍 Testing Redis from Django container..."
docker compose -f docker-compose.production.yml exec django python -c "
import redis
import os
redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
r = redis.from_url(redis_url)
print('Redis connection successful!')
print('Redis info:', r.info()['redis_version'])
"

# Test Django cache
echo "💾 Testing Django cache..."
docker compose -f docker-compose.production.yml exec django python manage.py shell -c "
from django.core.cache import cache
cache.set('test_key', 'test_value', 30)
result = cache.get('test_key')
print('Cache test:', 'SUCCESS' if result == 'test_value' else 'FAILED')
"

echo "✅ Redis tests completed!"
