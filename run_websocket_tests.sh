#!/bin/bash
# Run WebSocket Authentication Tests with proper environment setup

set -e

# Activate virtual environment
source venv/bin/activate

# Set Vault connection
export VAULT_ADDR=http://localhost:8200
export VAULT_ROOT_TOKEN=dev-only-token-change-in-prod

# Get JWT secret from Vault
echo "Fetching JWT secret from Vault..."
JWT_SECRET=$(python -c "
import hvac
client = hvac.Client(url='http://localhost:8200', token='dev-only-token-change-in-prod')
secret = client.secrets.kv.v2.read_secret_version(path='amc-simulation/api-keys')
print(secret['data']['data']['jwt_secret'])
")

# Set environment variables
export SECRET_KEY=$JWT_SECRET
export REDIS_URL=redis://localhost:7379

echo "Running WebSocket authentication tests..."
pytest backend/tests/test_websocket_auth.py -v --tb=short
