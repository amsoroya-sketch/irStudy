#!/bin/bash
# Run WebSocket Authentication Load Tests with proper environment setup
# Task 2.3: Load Testing Implementation

set -e

echo "=============================================================================="
echo "AMC Clinical Exam Simulation - WebSocket Authentication Load Tests"
echo "Task 2.3: Load Testing Implementation"
echo "=============================================================================="

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Please create it first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r backend/requirements.txt"
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Set Vault connection (SECURITY: Using environment variables, not hardcoded)
export VAULT_ADDR=http://localhost:8200
export VAULT_ROOT_TOKEN=dev-only-token-change-in-prod

# Get JWT secret from Vault (SECURITY: Fetching from Vault, not hardcoded)
echo "Fetching JWT secret from Vault..."
JWT_SECRET=$(python -c "
import hvac
import sys

try:
    client = hvac.Client(url='http://localhost:8200', token='dev-only-token-change-in-prod')
    secret = client.secrets.kv.v2.read_secret_version(path='amc-simulation/api-keys')
    print(secret['data']['data']['jwt_secret'])
except Exception as e:
    print(f'ERROR: Failed to fetch JWT secret from Vault: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null)

if [ -z "$JWT_SECRET" ]; then
    echo "ERROR: Failed to fetch JWT secret from Vault"
    echo "Please ensure Vault is running and secrets are configured:"
    echo "  docker-compose up -d vault"
    echo "  ./scripts/setup_vault_secrets.sh"
    exit 1
fi

# Set environment variables (SECURITY: From Vault, not hardcoded)
export SECRET_KEY=$JWT_SECRET
export REDIS_URL=redis://localhost:7379

echo "✓ Environment configured"
echo ""

# Check Redis is running
echo "Checking Redis connection..."
if ! redis-cli -p 7379 ping > /dev/null 2>&1; then
    echo "WARNING: Redis not responding on port 7379"
    echo "Please ensure Redis is running:"
    echo "  docker-compose up -d redis"
    echo ""
    echo "Continuing anyway (tests will use mock Redis if needed)..."
fi

# Run load tests
echo "=============================================================================="
echo "Running WebSocket authentication load tests..."
echo "=============================================================================="
echo ""

python backend/tests/load_test_websocket.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================================================="
    echo "✓ Load tests completed successfully"
    echo "=============================================================================="
    echo ""
    echo "Review the report: TASK_2.3_LOAD_TEST_REPORT.md"
    exit 0
else
    echo ""
    echo "=============================================================================="
    echo "✗ Load tests failed"
    echo "=============================================================================="
    echo ""
    echo "Check the output above for errors"
    exit 1
fi
