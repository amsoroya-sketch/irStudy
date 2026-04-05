#!/bin/bash
# Start irStudy Backend with proper environment variables

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Check if PostgreSQL is running
if ! pg_isready -h $DATABASE_HOST -p $DATABASE_PORT > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running on ${DATABASE_HOST}:${DATABASE_PORT}"
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
    sleep 2
fi

# Verify database password is set
if [ -z "$DATABASE_PASSWORD" ]; then
    echo "❌ DATABASE_PASSWORD not set"
    exit 1
fi

echo "✅ DATABASE_PASSWORD loaded"
echo "✅ Starting backend on http://localhost:8001"
echo ""

# Start backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
