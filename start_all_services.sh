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

# Backend deps live in backend/venv (the global uvicorn is missing prometheus_client).
if [ ! -x "backend/venv/bin/uvicorn" ]; then
    echo -e "${RED}❌ backend/venv not found. Creating...${NC}"
    python3 -m venv backend/venv
    backend/venv/bin/pip install -r backend/requirements.txt
fi

# Environment comes from backend/.env (DB password, JWT secret, CORS, ANTHROPIC_API_KEY).
export $(grep -v '^#' backend/.env | xargs)

# Kill any existing backend process
pkill -f "venv/bin/uvicorn src.main:app" || true

# Start backend in background — MUST pin :8001 (the frontend hardcodes localhost:8001,
# and :8000 is taken by an unrelated container).
cd backend
nohup venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8001 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}   Backend logs: tail -f logs/backend.log${NC}"
echo -e "${BLUE}   Backend API: http://localhost:8001 (health: /health, docs: /api/docs)${NC}"
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
echo -e "${BLUE}   Frontend URL: http://localhost:5173${NC}"
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ All services started!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${BLUE}Services:${NC}"
echo -e "  🗄️  PostgreSQL: localhost:5433"
echo -e "  💾 Redis: localhost:6380"
echo -e "  🔍 Qdrant: localhost:6333"
echo -e "  🚀 Backend API: http://localhost:8001"
echo -e "  🎨 Frontend: http://localhost:5173"
echo ""

echo -e "${BLUE}Useful commands:${NC}"
echo -e "  View backend logs:  tail -f logs/backend.log"
echo -e "  View frontend logs: tail -f logs/frontend.log"
echo -e "  Stop all services:  ./stop_all_services.sh"
echo -e "  Check status:       docker ps | grep irstudy"
echo ""

echo -e "${YELLOW}Note: Backend and frontend are running in background.${NC}"
echo -e "${YELLOW}To stop them, use: pkill -f 'uvicorn.*src.main:app' && pkill -f 'vite'${NC}\n"
