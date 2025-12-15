#!/bin/bash
# Medical Education AI System - Setup Script
# Automated installation and configuration

set -e  # Exit on error

echo "========================================="
echo "Medical Education AI System Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This script is designed for Linux${NC}"
    exit 1
fi

# Check for NVIDIA GPU
echo -e "${YELLOW}Checking for NVIDIA GPU...${NC}"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi | grep "CUDA Version"
    echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
else
    echo -e "${RED}Warning: nvidia-smi not found. GPU acceleration may not work.${NC}"
fi

# Check for Python 3.11+
echo -e "${YELLOW}Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}Error: Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check for Docker
echo -e "${YELLOW}Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ $DOCKER_VERSION found${NC}"
else
    echo -e "${RED}Error: Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check for Docker Compose
echo -e "${YELLOW}Checking Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓ $COMPOSE_VERSION found${NC}"
else
    echo -e "${RED}Error: Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check for Ollama
echo -e "${YELLOW}Checking Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama found${NC}"
    ollama list
else
    echo -e "${YELLOW}Ollama not found. Installing...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed${NC}"
fi

# Create virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Install Tesseract OCR
echo -e "${YELLOW}Installing Tesseract OCR...${NC}"
if command -v tesseract &> /dev/null; then
    echo -e "${GREEN}✓ Tesseract already installed${NC}"
else
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr
    echo -e "${GREEN}✓ Tesseract OCR installed${NC}"
fi

# Create data directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p data/{pdfs/{australian,core,specialties,free},processed,embeddings,raw}
mkdir -p docker/{qdrant_storage,neo4j_data,neo4j_logs,neo4j_import,postgres_data,redis_data,prometheus_data,grafana_data}
echo -e "${GREEN}✓ Data directories created${NC}"

# Download recommended Ollama models
echo -e "${YELLOW}Downloading recommended Ollama models...${NC}"
echo "This may take a while (several GB)..."

models=("meditron:7b" "biomistral:7b" "llama3.1:70b" "mixtral:8x7b")

for model in "${models[@]}"; do
    if ollama list | grep -q "$model"; then
        echo -e "${GREEN}✓ $model already downloaded${NC}"
    else
        echo -e "${YELLOW}Downloading $model...${NC}"
        ollama pull "$model"
        echo -e "${GREEN}✓ $model downloaded${NC}"
    fi
done

# Start Docker services
echo -e "${YELLOW}Starting Docker services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Docker services started${NC}"

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready (30 seconds)...${NC}"
sleep 30

# Check service status
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Place your medical textbook PDFs in data/pdfs/"
echo "2. Run: python scripts/extract_pdfs.py"
echo "3. Run: python scripts/chunk_medical_texts.py"
echo "4. Run: python scripts/generate_embeddings.py"
echo "5. Run: python scripts/index_qdrant.py"
echo ""
echo "Access points:"
echo "- Qdrant: http://localhost:6333/dashboard"
echo "- Neo4j: http://localhost:7474 (neo4j/medical_ai_password_2025)"
echo "- Grafana: http://localhost:3001 (admin/medical_admin_2025)"
echo "- Prometheus: http://localhost:9090"
echo ""
echo "Read README.md for detailed instructions."
echo ""
