#!/bin/bash
# Test runner script with environment variables

# Activate virtual environment
source venv/bin/activate

# Set environment variables for testing
export DATABASE_PASSWORD="test"
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export SECRET_KEY="$JWT_SECRET_KEY"
export DATABASE_URL="sqlite:///:memory:"
export ENVIRONMENT="test"

# Run tests
python -m pytest tests/test_api/test_study_cards.py "$@"
