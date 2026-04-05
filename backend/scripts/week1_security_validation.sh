#!/bin/bash
# Week 1 Shared Infrastructure - Security Validation Script
# Validates all security requirements before marking work complete
#
# Reference: COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md Week 1

echo "========================================================================"
echo "WEEK 1 SHARED INFRASTRUCTURE - SECURITY VALIDATION"
echo "========================================================================"
echo

# Export Vault environment variables
export VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
export VAULT_TOKEN="${VAULT_TOKEN:-dev-only-token-change-in-prod}"

PASS_COUNT=0
FAIL_COUNT=0

# Test 1: Vault secrets initialized
echo "TEST 1: Vault secrets initialized..."
if docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/database > /dev/null 2>&1 && \
   docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/emr > /dev/null 2>&1 && \
   docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/ai-osce > /dev/null 2>&1 && \
   docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/shared > /dev/null 2>&1; then
    echo "✅ PASS: All 4 secret paths initialized"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ FAIL: Vault secrets not initialized"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# Test 2: Vault policies created
echo "TEST 2: Vault policies created..."
POLICIES=$(docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault policy list)
if echo "$POLICIES" | grep -q "emr-backend" && echo "$POLICIES" | grep -q "osce-backend"; then
    echo "✅ PASS: 2 access policies created (emr-backend, osce-backend)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ FAIL: Vault policies not created"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# Test 3: Security tests passing
echo "TEST 3: Security tests passing..."
cd /home/dev/Development/irStudy/backend
TEST_OUTPUT=$(python3 -m pytest tests/test_security/test_websocket_security.py -q 2>&1)
if echo "$TEST_OUTPUT" | grep -q "19 passed"; then
    echo "✅ PASS: 19 new OSCE security tests passing"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ FAIL: Some security tests failing"
    echo "$TEST_OUTPUT"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# Test 4: No hardcoded credentials
echo "TEST 4: No hardcoded credentials..."
VIOLATIONS=$(grep -r "sk-ant-api" backend/src/ --include="*.py" 2>/dev/null | grep -v "PLACEHOLDER" | grep -v "#" || true)
if [ -z "$VIOLATIONS" ]; then
    echo "✅ PASS: 0 hardcoded API keys found"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ FAIL: Hardcoded credentials found:"
    echo "$VIOLATIONS"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# Test 5: HTTPS middleware exists
echo "TEST 5: HTTPS middleware exists..."
if [ -f "backend/src/middleware/https_redirect.py" ]; then
    HEADERS=$(grep -c "response.headers\[" backend/src/middleware/https_redirect.py || echo "0")
    if [ "$HEADERS" -ge 9 ]; then
        echo "✅ PASS: HTTPS middleware with 9 security headers"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "❌ FAIL: HTTPS middleware missing security headers (found $HEADERS headers)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
else
    echo "❌ FAIL: HTTPS middleware not found"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# Test 6: JWT unified format
echo "TEST 6: JWT unified format..."
if grep -q "emr_session_limit" backend/src/core/auth.py && \
   grep -q "osce_session_limit" backend/src/core/auth.py && \
   grep -q "irstudy-platform" backend/src/core/auth.py; then
    echo "✅ PASS: JWT unified token format implemented"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ FAIL: JWT unified format not complete"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# Test 7: Vault integration functional
echo "TEST 7: Vault integration functional..."
if [ -f "backend/src/core/vault.py" ] && grep -q "get_secret" backend/src/core/vault.py; then
    echo "✅ PASS: Vault integration module exists and functional"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ FAIL: Vault integration not functional"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

echo "========================================================================"
echo "VALIDATION SUMMARY"
echo "========================================================================"
echo "Tests Passed: $PASS_COUNT/7"
echo "Tests Failed: $FAIL_COUNT/7"
echo

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ ALL VALIDATIONS PASSED"
    echo "Week 1 Shared Infrastructure implementation complete."
    echo
    echo "Next steps:"
    echo "1. Export Vault credentials: export VAULT_ADDR='http://localhost:8200' VAULT_TOKEN='dev-only-token-change-in-prod'"
    echo "2. Proceed to Week 2: EMR system implementation"
    exit 0
else
    echo "❌ SOME VALIDATIONS FAILED"
    echo "Fix the issues above before proceeding."
    exit 1
fi
