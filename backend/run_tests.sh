#!/bin/bash
# Test runner script with all required environment variables

export PYTHONPATH=/home/dev/Development/irStudy/backend
export VAULT_ADDR='http://localhost:8200'
export VAULT_ROOT_TOKEN='dev-only-token-change-in-prod'
export DATABASE_PASSWORD='test-db-password-for-pytest'
export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"  # ephemeral test key; never hardcode
export DATABASE_URL='sqlite:///./test_progress.db'
export ENVIRONMENT='test'

cd /home/dev/Development/irStudy/backend
venv/bin/pytest -v --tb=short "$@"
