#!/bin/bash
# Run Task 3.1 User Verification Tests

set -e

# Activate virtual environment
source venv/bin/activate

# Set Vault connection
export VAULT_ADDR=http://localhost:8200
export VAULT_ROOT_TOKEN=dev-only-token-change-in-prod

# Get secrets from Vault
echo "Fetching secrets from Vault..."
SECRETS=$(python -c "
import hvac
client = hvac.Client(url='http://localhost:8200', token='dev-only-token-change-in-prod')
api_keys = client.secrets.kv.v2.read_secret_version(path='amc-simulation/api-keys')
db_creds = client.secrets.kv.v2.read_secret_version(path='amc-simulation/database')
print(f\"{api_keys['data']['data']['jwt_secret']}|{db_creds['data']['data']['password']}\")
" 2>/dev/null)

JWT_SECRET=$(echo $SECRETS | cut -d'|' -f1)
DB_PASSWORD=$(echo $SECRETS | cut -d'|' -f2)

# Set environment variables
export SECRET_KEY=$JWT_SECRET
export REDIS_URL=redis://localhost:7379
export DATABASE_PASSWORD=$DB_PASSWORD
export DATABASE_USER=amc_user
export DATABASE_HOST=localhost
export DATABASE_PORT=5433
export DATABASE_NAME=amc_simulation

echo "Running Task 3.1 User Verification tests..."
cd backend
pytest tests/test_user_verification.py -v --tb=short
