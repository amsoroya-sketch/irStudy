#!/bin/bash
# Run tests that depend on Vault with proper environment setup

set -a  # Auto-export all variables
source .env.test
set +a

# Ensure Vault is running
echo "🔍 Checking Vault status..."
if ! curl -s http://localhost:8200/v1/sys/health > /dev/null 2>&1; then
    echo "❌ Vault not running. Starting Vault..."
    bash scripts/start_vault_dev.sh
    bash scripts/init_vault_secrets.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run user verification tests
echo ""
echo "========================================================================"
echo "🧪 Running User Verification Tests (12 tests)"
echo "========================================================================"
pytest tests/test_user_verification.py -v --tb=short

USER_VERIFICATION_EXIT=$?

# Run websocket auth tests
echo ""
echo "========================================================================"
echo "🧪 Running WebSocket Authentication Tests (10 tests)"
echo "========================================================================"
pytest tests/test_websocket_auth.py -v --tb=short

WEBSOCKET_AUTH_EXIT=$?

# Print summary
echo ""
echo "========================================================================"
echo "📊 TEST SUMMARY"
echo "========================================================================"
if [ $USER_VERIFICATION_EXIT -eq 0 ]; then
    echo "✅ User Verification Tests: PASSED (12/12)"
else
    echo "❌ User Verification Tests: FAILED"
fi

if [ $WEBSOCKET_AUTH_EXIT -eq 0 ]; then
    echo "✅ WebSocket Auth Tests: PASSED (10/10)"
else
    echo "❌ WebSocket Auth Tests: FAILED"
fi

# Exit with failure if either test suite failed
if [ $USER_VERIFICATION_EXIT -ne 0 ] || [ $WEBSOCKET_AUTH_EXIT -ne 0 ]; then
    echo ""
    echo "❌ Some tests failed. Expected: 22/22 passing"
    exit 1
fi

echo ""
echo "✅ All Vault-dependent tests passing: 22/22"
exit 0
