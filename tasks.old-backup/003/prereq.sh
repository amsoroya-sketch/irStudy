#!/bin/bash
# Task 003 Prerequisite: Start Docker Stack
# This starts the 11-service Docker stack needed for Task 019 (RAG/Qdrant)

set -e
cd /home/dev/Development/irStudy

echo "🐳 Starting Docker stack (11 services)..."
docker compose up -d

echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

echo "✅ Docker stack started. Running health checks..."
docker compose ps

echo ""
echo "🔍 Testing service connectivity..."

# Test PostgreSQL
echo -n "PostgreSQL: "
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "SELECT 1;" > /dev/null 2>&1 && echo "✅" || echo "❌"

# Test Redis
echo -n "Redis: "
docker exec irstudy-redis redis-cli ping > /dev/null 2>&1 && echo "✅" || echo "❌"

# Test Qdrant (needed for Task 019)
echo -n "Qdrant (vector DB): "
curl -s http://localhost:6333/healthz > /dev/null 2>&1 && echo "✅" || echo "❌"

echo ""
echo "✅ Docker stack is ready!"
echo "⚠️  Run './tasks/003/verify.sh' to confirm all services are healthy"
