#!/bin/bash
set -e

cd /home/dev/Development/irStudy/backend
source ../venv/bin/activate

export SECRET_KEY="test_secret_key_for_testing_12345678901234567890123456789012345678901234567890"
export DATABASE_PASSWORD="test"
export DATABASE_URL="sqlite:///:memory:"
export ENVIRONMENT="test"

echo "Running AI OSCE API tests..."
python -m pytest tests/test_api/test_ai_osce.py -v --tb=short
