#!/bin/bash
# Run EMR API tests with proper environment setup

# Set environment variables
export PYTHONPATH=/home/dev/Development/irStudy/backend
export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"  # ephemeral test key; never hardcode
export DATABASE_URL="sqlite:///./test_progress.db"
export DATABASE_PASSWORD="test_password"
export ACCESS_TOKEN_EXPIRE_MINUTES=30

# Disable Vault for tests (use env vars instead)
export VAULT_ADDR="http://localhost:8200"
export VAULT_ROOT_TOKEN="dev-only-token"

# Run tests
venv/bin/pytest tests/test_api/test_emr/test_emr_sessions.py -v --tb=short "$@"
