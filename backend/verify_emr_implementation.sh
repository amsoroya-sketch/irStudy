#!/bin/bash
# Final verification script for PRD_GAP_002

echo "=========================================="
echo "PRD_GAP_002: EMR API Endpoints Verification"
echo "=========================================="
echo ""

echo "1. Checking file structure..."
echo "   EMR API directory:"
ls -la src/api/v1/emr/*.py | awk '{print "     - " $9}'
echo ""

echo "2. Counting endpoints..."
ENDPOINT_COUNT=$(grep -r "@router\." src/api/v1/emr/*.py | grep -E "(get|post|put|delete|patch)" | wc -l)
echo "   Total endpoints found: $ENDPOINT_COUNT"
echo ""

echo "3. Running integration tests..."
export PYTHONPATH=/home/dev/Development/irStudy/backend
export SECRET_KEY="eb61d3eecfd9ed9bc71c388675b36105b54692fea0f1d34c568b56e5bf88f20d"
export DATABASE_URL="sqlite:///./test_progress.db"
venv/bin/pytest tests/test_api/test_emr_api.py -v --tb=short -q 2>&1 | tail -5
echo ""

echo "4. Checking for hardcoded credentials..."
CREDS=$(grep -rn "sk-ant-\|password\s*=" src/api/v1/emr/ | wc -l)
if [ $CREDS -eq 0 ]; then
    echo "   ✅ No hardcoded credentials found"
else
    echo "   ❌ WARNING: $CREDS hardcoded credentials found"
fi
echo ""

echo "5. Verifying router registration..."
ROUTER_REG=$(grep -c "emr_router" src/api/v1/router.py)
if [ $ROUTER_REG -gt 0 ]; then
    echo "   ✅ EMR router registered in main router"
else
    echo "   ❌ EMR router NOT registered"
fi
echo ""

echo "=========================================="
echo "VERIFICATION COMPLETE"
echo "=========================================="
