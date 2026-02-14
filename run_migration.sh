#!/bin/bash
# Apply Task 3.1 database migration

set -e

# Activate virtual environment
source venv/bin/activate

# Set Vault connection
export VAULT_ADDR=http://localhost:8200
export VAULT_ROOT_TOKEN=dev-only-token-change-in-prod

# Get database password from Vault
echo "Fetching database password from Vault..."
DB_PASSWORD=$(python -c "
import hvac
client = hvac.Client(url='http://localhost:8200', token='dev-only-token-change-in-prod')
secret = client.secrets.kv.v2.read_secret_version(path='amc-simulation/database')
print(secret['data']['data']['password'])
" 2>/dev/null)

# Set database environment variables
export DATABASE_PASSWORD=$DB_PASSWORD
export DATABASE_USER=amc_user
export DATABASE_HOST=localhost
export DATABASE_PORT=5433
export DATABASE_NAME=amc_simulation

echo "Applying database migrations..."
cd backend
alembic upgrade head

echo "Migration complete!"
