#!/bin/bash
#
# Stop All IRStudy Services
# =========================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Stopping IRStudy Services${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Stop backend
echo -e "${YELLOW}Stopping Backend FastAPI server...${NC}"
pkill -f "uvicorn.*main:app" && echo -e "${GREEN}✅ Backend stopped${NC}" || echo -e "${YELLOW}⚠️  No backend process found${NC}"

# Stop frontend
echo -e "${YELLOW}Stopping Frontend Vite server...${NC}"
pkill -f "vite" && echo -e "${GREEN}✅ Frontend stopped${NC}" || echo -e "${YELLOW}⚠️  No frontend process found${NC}"

# Stop Docker containers
echo -e "${YELLOW}Stopping Docker containers...${NC}"
docker compose down

echo -e "\n${GREEN}✅ All services stopped${NC}\n"
