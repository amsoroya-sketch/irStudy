#!/bin/bash
#
# Start All IRStudy Services
# ==========================
#
# This script starts all services needed for the IRStudy application:
# - Docker containers (PostgreSQL, Redis, Qdrant)
# - Backend FastAPI server
# - Frontend Vite development server

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting IRStudy Services${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 1. Start Docker containers
echo -e "${YELLOW}[1/3] Starting Docker containers...${NC}"
docker compose up -d postgres redis qdrant

# Wait for containers to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 5

# Check health
if docker ps | grep -q "irstudy-postgres.*healthy"; then
    echo -e "${GREEN}✅ PostgreSQL is healthy${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not healthy${NC}"
fi

if docker ps | grep -q "irstudy-redis.*healthy"; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis is not healthy${NC}"
fi

if docker ps | grep -q "irstudy-qdrant.*healthy"; then
    echo -e "${GREEN}✅ Qdrant is healthy${NC}"
else
    echo -e "${RED}❌ Qdrant is not healthy${NC}"
fi

echo ""

# 2. Start Backend Server (in background)
echo -e "${YELLOW}[2/3] Starting Backend FastAPI server...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r backend/requirements.txt
else
    source venv/bin/activate
fi

# Set environment variables
export DATABASE_PASSWORD="$(cat secrets/db_password.txt)"
export DATABASE_HOST="localhost"
export DATABASE_PORT="5433"
export DATABASE_NAME="irstudy_medical"
export SECRET_KEY="$(cat secrets/jwt_secret.txt)"
export REDIS_URL="redis://localhost:6380"
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"

# Kill any existing backend process
pkill -f "uvicorn.*main:app" || true

# Start backend in background
cd backend
nohup uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}   Backend logs: tail -f logs/backend.log${NC}"
echo -e "${BLUE}   Backend API: http://localhost:8000${NC}"
echo ""

# Wait for backend to start
sleep 3

# 3. Start Frontend Server (in background)
echo -e "${YELLOW}[3/3] Starting Frontend Vite server...${NC}"

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Kill any existing frontend process
pkill -f "vite" || true

# Create logs directory if it doesn't exist
mkdir -p logs

# Start frontend in background
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "${BLUE}   Frontend logs: tail -f logs/frontend.log${NC}"
echo -e "${BLUE}   Frontend URL: http://localhost:5174${NC}"
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ All services started!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${BLUE}Services:${NC}"
echo -e "  🗄️  PostgreSQL: localhost:5433"
echo -e "  💾 Redis: localhost:6380"
echo -e "  🔍 Qdrant: localhost:6333"
echo -e "  🚀 Backend API: http://localhost:8000"
echo -e "  🎨 Frontend: http://localhost:5174"
echo ""

echo -e "${BLUE}Useful commands:${NC}"
echo -e "  View backend logs:  tail -f logs/backend.log"
echo -e "  View frontend logs: tail -f logs/frontend.log"
echo -e "  Stop all services:  ./stop_all_services.sh"
echo -e "  Check status:       docker ps | grep irstudy"
echo ""

echo -e "${YELLOW}Note: Backend and frontend are running in background.${NC}"
echo -e "${YELLOW}To stop them, use: pkill -f 'uvicorn.*main:app' && pkill -f 'vite'${NC}\n"
