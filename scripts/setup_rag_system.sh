#!/bin/bash
################################################################################
# RAG System Setup Script
# Installs all dependencies needed for medical resource indexing and search
################################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="/home/dev/Development/irStudy"
VENV_PATH="${PROJECT_ROOT}/venv"

echo -e "${BLUE}=========================================================================${NC}"
echo -e "${BLUE}  RAG System Setup - Medical Resource Indexing${NC}"
echo -e "${BLUE}=========================================================================${NC}"
echo ""

# Check Python version
echo -e "${BLUE}1. Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}✗ Python 3.11+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check Docker
echo -e "${BLUE}2. Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo -e "${YELLOW}Install Docker: https://docs.docker.com/engine/install/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Create/activate virtual environment
echo -e "${BLUE}3. Setting up Python virtual environment...${NC}"
cd "$PROJECT_ROOT"

if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Virtual environment ready${NC}"

# Upgrade pip
echo -e "${BLUE}4. Upgrading pip...${NC}"
python3 -m pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install core dependencies
echo -e "${BLUE}5. Installing Python dependencies (this may take 10-15 minutes)...${NC}"
echo -e "${YELLOW}Installing: qdrant-client, sentence-transformers, torch, transformers${NC}"

# Install PyTorch first (CPU version for faster install)
echo "Installing PyTorch CPU version..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install from requirements.txt (skip torch since we already installed it)
echo "Installing remaining dependencies..."
pip install -r requirements.txt --no-deps || true
pip install -r requirements.txt

echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Start Qdrant vector database
echo -e "${BLUE}6. Setting up Qdrant vector database...${NC}"

# Check if Qdrant is already running
if docker ps | grep -q qdrant; then
    echo -e "${YELLOW}Qdrant already running${NC}"
else
    # Check if container exists but stopped
    if docker ps -a | grep -q qdrant; then
        echo "Starting existing Qdrant container..."
        docker start qdrant
    else
        echo "Creating new Qdrant container..."
        docker run -d \
            --name qdrant \
            -p 6333:6333 \
            -p 6334:6334 \
            -v $(pwd)/qdrant_storage:/qdrant/storage \
            qdrant/qdrant:latest
    fi
fi

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to start..."
sleep 5

# Test Qdrant connection
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Qdrant running at http://localhost:6333${NC}"
else
    echo -e "${RED}✗ Qdrant failed to start${NC}"
    echo "Check logs: docker logs qdrant"
    exit 1
fi

# Download sentence-transformer model
echo -e "${BLUE}7. Downloading PubMedBERT embedding model (first time only, ~420MB)...${NC}"
python3 << 'EOF'
from sentence_transformers import SentenceTransformer
import os

# Download model to cache
model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
print(f"Downloading {model_name}...")
model = SentenceTransformer(model_name)
# Get cache directory from huggingface_hub
try:
    from huggingface_hub import snapshot_download
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    print(f"✓ Model downloaded to HuggingFace cache: {cache_dir}")
except:
    print("✓ Model downloaded successfully")
EOF

echo -e "${GREEN}✓ PubMedBERT model ready${NC}"

# Create necessary directories
echo -e "${BLUE}8. Creating directories...${NC}"
mkdir -p embeddings
mkdir -p qdrant_storage
mkdir -p validation_reports
mkdir -p logs/rag
echo -e "${GREEN}✓ Directories created${NC}"

# Test installation
echo -e "${BLUE}9. Testing installation...${NC}"

python3 << 'EOF'
import sys

try:
    # Test imports
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer
    import torch
    from transformers import AutoTokenizer

    # Test Qdrant connection
    client = QdrantClient(url="http://localhost:6333")
    collections = client.get_collections()

    # Test model loading
    model = SentenceTransformer("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")

    # Test embedding
    test_text = "Acute myocardial infarction is a medical emergency."
    embedding = model.encode(test_text)

    print(f"✓ Qdrant: {len(collections.collections)} collections")
    print(f"✓ PubMedBERT: {len(embedding)}-dimensional embeddings")
    print(f"✓ PyTorch: {torch.__version__}")
    print("✓ All components working!")

except Exception as e:
    print(f"✗ Test failed: {e}", file=sys.stderr)
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation test passed${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    exit 1
fi

# Summary
echo ""
echo -e "${GREEN}=========================================================================${NC}"
echo -e "${GREEN}  RAG System Setup Complete!${NC}"
echo -e "${GREEN}=========================================================================${NC}"
echo ""
echo -e "${BLUE}Services Running:${NC}"
echo "  • Qdrant Vector DB: http://localhost:6333"
echo "  • Qdrant Dashboard: http://localhost:6333/dashboard"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Activate virtual environment:"
echo "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "  2. Process and embed your documents:"
echo "     ${YELLOW}python3 scripts/embed_medical_resources.py --input /mnt/data/medical_resources/${NC}"
echo ""
echo "  3. Index embeddings to Qdrant:"
echo "     ${YELLOW}python3 scripts/index_qdrant.py --embeddings embeddings/medical_embeddings.pkl${NC}"
echo ""
echo "  4. Test RAG search:"
echo "     ${YELLOW}python3 scripts/test_rag_search.py --query \"acute myocardial infarction diagnosis\"${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  • Stop Qdrant: ${YELLOW}docker stop qdrant${NC}"
echo "  • Start Qdrant: ${YELLOW}docker start qdrant${NC}"
echo "  • View logs: ${YELLOW}docker logs qdrant${NC}"
echo "  • Check status: ${YELLOW}curl http://localhost:6333/collections${NC}"
echo ""
echo -e "${GREEN}Setup completed successfully!${NC}"
