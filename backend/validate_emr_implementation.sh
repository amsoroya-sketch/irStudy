#!/bin/bash

# EMR Sessions API Validation Script
# Tests all 29 endpoints to ensure 100% pass rate

set -e

echo "======================================"
echo "EMR Sessions API Validation"
echo "======================================"
echo ""

# Change to backend directory
cd /home/dev/Development/irStudy/backend

# Activate virtual environment
source venv/bin/activate

# Set required environment variables
export DATABASE_PASSWORD="test_password"
export SECRET_KEY="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

echo "Running EMR Sessions API Tests..."
echo ""

# Run tests with verbose output
python -m pytest tests/test_api/test_emr/test_emr_sessions.py -v --tb=short

echo ""
echo "======================================"
echo "Validation Complete"
echo "======================================"
