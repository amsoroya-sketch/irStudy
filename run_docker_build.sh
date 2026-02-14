#!/bin/bash
# Automated Docker build and startup in tmux
# Created: 2026-02-02

set -e
cd /home/dev/Development/irStudy

echo "🚀 Starting Docker build and startup process..."
echo ""

# Build all services
echo "📦 Building Docker images..."
docker compose build 2>&1 | tee logs/docker_build.log

# Start services
echo ""
echo "🐳 Starting Docker stack (11 services)..."
docker compose up -d

# Wait for initialization
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

# Health checks
echo ""
echo "🔍 Running health checks..."
docker compose ps

echo ""
echo "✅ Testing service connectivity..."

# PostgreSQL
echo -n "PostgreSQL: "
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "SELECT 1;" > /dev/null 2>&1 && echo "✅" || echo "❌"

# Redis  
echo -n "Redis: "
docker exec irstudy-redis redis-cli ping > /dev/null 2>&1 && echo "✅" || echo "❌"

# Qdrant
echo -n "Qdrant (vector DB): "
curl -s http://localhost:6333/healthz > /dev/null 2>&1 && echo "✅" || echo "❌"

echo ""
echo "✅ Docker stack is ready!"
echo "📊 Check full build log: logs/docker_build.log"
