#!/bin/bash
# Test runner script with all required environment variables

export PYTHONPATH=/home/dev/Development/irStudy/backend
export VAULT_ADDR='http://localhost:8200'
export VAULT_ROOT_TOKEN='dev-only-token-change-in-prod'
export DATABASE_PASSWORD='test-db-password-for-pytest'
export SECRET_KEY='91f7e4919717fb5549b845e6ccc79fcd1e822b792b31bf660d359aa17e2dd306'
export DATABASE_URL='sqlite:///./test_progress.db'
export ENVIRONMENT='test'

cd /home/dev/Development/irStudy/backend
venv/bin/pytest -v --tb=short "$@"
