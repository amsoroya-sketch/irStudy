#!/bin/bash
# Task 003 Verification: Check Docker Stack Health

cd /home/dev/Development/irStudy

echo "🔍 Verifying Docker stack health..."

# Check if all services are running
RUNNING=$(docker compose ps --services --filter "status=running" | wc -l)
TOTAL=$(docker compose ps --services | wc -l)

echo "Services running: $RUNNING/$TOTAL"

if [ "$RUNNING" -eq 11 ]; then
    echo "✅ All 11 services are healthy"
    
    # Check Qdrant specifically (needed for Task 019)
    if curl -s http://localhost:6333/healthz > /dev/null 2>&1; then
        echo "✅ Qdrant vector database is accessible (Task 019 prerequisite met)"
        exit 0
    else
        echo "❌ Qdrant is not accessible"
        exit 1
    fi
else
    echo "❌ Not all services are running"
    docker compose ps
    exit 1
fi
