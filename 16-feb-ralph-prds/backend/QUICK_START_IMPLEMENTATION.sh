#!/bin/bash

##############################################################################
# Critical Backend Fixes - Quick Start Implementation Script
#
# Date: 2026-02-16
# Purpose: Automated setup for all 12 critical fixes
# Usage: bash QUICK_START_IMPLEMENTATION.sh
#
# IMPORTANT: This script ONLY creates file structure and installs dependencies.
# You must manually copy code from CRITICAL_FIXES_IMPLEMENTATION_SUMMARY.md
##############################################################################

set -e  # Exit on error

echo "=========================================="
echo "EMR Backend Critical Fixes - Quick Start"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to backend directory
cd /home/dev/Development/irStudy/backend

echo -e "${YELLOW}Step 1: Creating new file structure...${NC}"

# Create security module (FIX #2: Encryption)
mkdir -p src/security
touch src/security/__init__.py
touch src/security/encryption.py
echo -e "${GREEN}✓ Created src/security/encryption.py${NC}"

# Create validators (FIX #3: Fallback)
mkdir -p src/services/emr/validators
touch src/services/emr/validators/__init__.py
touch src/services/emr/validators/base.py
touch src/services/emr/validators/fallback_validator.py
echo -e "${GREEN}✓ Created validators directory${NC}"

# Create health checks (FIX #9)
touch src/api/v1/health.py
echo -e "${GREEN}✓ Created src/api/v1/health.py${NC}"

# Create test fixtures (FIX #11: Benchmarking)
mkdir -p tests/fixtures
touch tests/fixtures/gold_standard_soap_notes.json
touch tests/test_ai_validation_accuracy.py
echo -e "${GREEN}✓ Created test fixtures and benchmark tests${NC}"

echo ""
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Install new dependencies
pip install hvac==1.2.1        # Vault client (FIX #2)
pip install slowapi==0.1.9     # Rate limiting (FIX #7)
pip install redis==5.0.1       # Caching + rate limiting (FIX #7)
pip install bandit==1.7.5      # Security scanning

echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 3: Creating Alembic migrations...${NC}"

# Migration 1: PHI Encryption
alembic revision -m "add_phi_encryption_columns" --rev-id="20260216_011"
echo -e "${GREEN}✓ Created migration: 20260216_011_add_phi_encryption_columns.py${NC}"

# Migration 2: Session constraints
alembic revision -m "add_max_active_sessions_constraint" --rev-id="20260216_012"
echo -e "${GREEN}✓ Created migration: 20260216_012_add_max_active_sessions_constraint.py${NC}"

echo ""
echo -e "${YELLOW}Step 4: Infrastructure setup (Docker)...${NC}"

# Check if Vault is running
if ! docker ps | grep -q vault; then
    echo -e "${YELLOW}Starting HashiCorp Vault...${NC}"
    docker run --cap-add=IPC_LOCK -d \
        --name=vault \
        -p 8200:8200 \
        -e 'VAULT_DEV_ROOT_TOKEN_ID=dev-root-token' \
        -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' \
        vault

    sleep 3  # Wait for Vault to start

    export VAULT_ADDR='http://localhost:8200'
    export VAULT_TOKEN='dev-root-token'

    # Store encryption key
    docker exec vault vault kv put secret/emr/encryption-keys \
        phi_encryption_key="$(openssl rand -base64 32)"

    echo -e "${GREEN}✓ Vault started and encryption key stored${NC}"
else
    echo -e "${GREEN}✓ Vault already running${NC}"
fi

# Check if Redis is running
if ! docker ps | grep -q redis; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    docker run -d \
        --name redis \
        -p 6379:6379 \
        redis:alpine

    echo -e "${GREEN}✓ Redis started${NC}"
else
    echo -e "${GREEN}✓ Redis already running${NC}"
fi

echo ""
echo -e "${YELLOW}Step 5: Creating environment variables...${NC}"

# Create .env.development file
cat > .env.development <<EOF
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/irstudy_medical

# Vault (Encryption Keys)
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=dev-root-token

# Redis (Rate Limiting + Caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# Claude API (AI Validation)
CLAUDE_API_KEY=\${CLAUDE_API_KEY}  # Set this from actual Vault

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=\$(openssl rand -base64 32)
EOF

echo -e "${GREEN}✓ Created .env.development${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}File structure setup complete!${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}NEXT STEPS (MANUAL):${NC}"
echo ""
echo "1. Copy code from CRITICAL_FIXES_IMPLEMENTATION_SUMMARY.md to files:"
echo "   - src/security/encryption.py (220 lines)"
echo "   - src/services/emr/validators/fallback_validator.py (180 lines)"
echo "   - src/api/v1/health.py (120 lines)"
echo "   - tests/fixtures/gold_standard_soap_notes.json (500 lines JSON)"
echo "   - tests/test_ai_validation_accuracy.py (150 lines)"
echo ""
echo "2. Update existing files:"
echo "   - src/api/v1/emr/sessions.py (submit transaction handling)"
echo "   - src/services/emr/claude_service.py (fallback + anonymization)"
echo "   - src/main.py (HTTPS + rate limiting)"
echo "   - src/schemas/emr.py (SessionDataValidator)"
echo ""
echo "3. Update Alembic migrations:"
echo "   - alembic/versions/20260216_011_*.py (pgcrypto + encryption)"
echo "   - alembic/versions/20260216_012_*.py (session constraint trigger)"
echo ""
echo "4. Run migrations:"
echo "   alembic upgrade head"
echo ""
echo "5. Run tests:"
echo "   pytest tests/ -v"
echo "   pytest tests/test_ai_validation_accuracy.py -v  # AI benchmark"
echo ""
echo "6. Security scan:"
echo "   bandit -r src/ -ll"
echo ""
echo "7. Load testing:"
echo "   # Install: pip install locust"
echo "   # Run: locust -f tests/load/test_submit_performance.py"
echo ""
echo -e "${YELLOW}Environment Variables to Set:${NC}"
echo "   export VAULT_ADDR=http://localhost:8200"
echo "   export VAULT_TOKEN=dev-root-token"
echo "   export CLAUDE_API_KEY=<your-actual-claude-api-key>"
echo ""
echo -e "${YELLOW}Docker Services Status:${NC}"
docker ps --filter "name=vault" --filter "name=redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "${GREEN}Ready for implementation!${NC}"
echo ""
echo "Reference documents:"
echo "  - CRITICAL_FIXES_IMPLEMENTATION_SUMMARY.md (full code)"
echo "  - FIXES_DELIVERY_SUMMARY.md (quick reference)"
echo ""
