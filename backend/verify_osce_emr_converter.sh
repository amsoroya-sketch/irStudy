#!/bin/bash

# OSCE-to-EMR Converter Implementation Verification Script
# Validates all components before deployment

set -e  # Exit on any error

BACKEND_DIR="/home/dev/Development/irStudy/backend"
cd "$BACKEND_DIR"

echo "=============================================="
echo "OSCE-to-EMR Converter Verification"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper function for checks
check() {
    local description="$1"
    local command="$2"
    local expected_pattern="$3"

    echo -n "Checking: $description... "

    if output=$(eval "$command" 2>&1); then
        if [[ -z "$expected_pattern" ]] || echo "$output" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}PASS${NC}"
            ((CHECKS_PASSED++))
            return 0
        else
            echo -e "${RED}FAIL${NC}"
            echo "  Expected pattern: $expected_pattern"
            echo "  Actual output: $output"
            ((CHECKS_FAILED++))
            return 1
        fi
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Command failed: $command"
        echo "  Output: $output"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo "=== 1. FILE STRUCTURE VALIDATION ==="
echo ""

check "Migration file exists" \
    "ls alembic/versions/20260405_1841_add_osce_emr_linking.py" \
    "20260405_1841_add_osce_emr_linking.py"

check "Integration schemas exist" \
    "ls src/schemas/integration.py" \
    "integration.py"

check "Converter service exists" \
    "ls src/services/integration/osce_to_emr_converter.py" \
    "osce_to_emr_converter.py"

check "API endpoint exists" \
    "ls src/api/v1/integration/converter.py" \
    "converter.py"

check "Test suite exists" \
    "ls tests/test_integration/test_osce_to_emr_converter.py" \
    "test_osce_to_emr_converter.py"

echo ""
echo "=== 2. CODE QUALITY VALIDATION ==="
echo ""

check "No hardcoded Claude API keys in converter" \
    "grep -c 'sk-ant-api' src/services/integration/osce_to_emr_converter.py || echo 0" \
    "^0$"

check "Vault integration present in converter" \
    "grep -c 'vault.get_secret' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "Australian terminology validation in schemas" \
    "grep -c 'paracetamol' src/schemas/integration.py" \
    "[1-9]"

check "PHI anonymization in converter" \
    "grep -c '_anonymize_phi' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "User authorization check in converter" \
    "grep -c 'not authorized' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

echo ""
echo "=== 3. LINE COUNT VALIDATION ==="
echo ""

migration_lines=$(wc -l < alembic/versions/20260405_1841_add_osce_emr_linking.py)
schemas_lines=$(wc -l < src/schemas/integration.py)
converter_lines=$(wc -l < src/services/integration/osce_to_emr_converter.py)
api_lines=$(wc -l < src/api/v1/integration/converter.py)
tests_lines=$(wc -l < tests/test_integration/test_osce_to_emr_converter.py)

echo "Migration file: $migration_lines lines (expected: ~85)"
echo "Integration schemas: $schemas_lines lines (expected: ~238)"
echo "Converter service: $converter_lines lines (expected: ~621)"
echo "API endpoint: $api_lines lines (expected: ~278)"
echo "Test suite: $tests_lines lines (expected: ~745)"

total_lines=$((migration_lines + schemas_lines + converter_lines + api_lines + tests_lines))
echo "Total implementation: $total_lines lines"

if [[ $total_lines -gt 1800 ]]; then
    echo -e "${GREEN}Line count PASS${NC} (comprehensive implementation)"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}Line count WARNING${NC} (may be incomplete)"
fi

echo ""
echo "=== 4. MIGRATION VALIDATION ==="
echo ""

check "Migration has upgrade function" \
    "grep -c 'def upgrade' alembic/versions/20260405_1841_add_osce_emr_linking.py" \
    "[1-9]"

check "Migration has downgrade function" \
    "grep -c 'def downgrade' alembic/versions/20260405_1841_add_osce_emr_linking.py" \
    "[1-9]"

check "Migration adds source_osce_attempt_id column" \
    "grep -c 'source_osce_attempt_id' alembic/versions/20260405_1841_add_osce_emr_linking.py" \
    "[2-9]"

check "Migration adds conversion_metadata column" \
    "grep -c 'conversion_metadata' alembic/versions/20260405_1841_add_osce_emr_linking.py" \
    "[2-9]"

check "Migration creates indexes" \
    "grep -c 'create_index' alembic/versions/20260405_1841_add_osce_emr_linking.py" \
    "[2-9]"

echo ""
echo "=== 5. SCHEMA VALIDATION ==="
echo ""

check "ConversionRequest schema defined" \
    "grep -c 'class ConversionRequest' src/schemas/integration.py" \
    "1"

check "ConversionResponse schema defined" \
    "grep -c 'class ConversionResponse' src/schemas/integration.py" \
    "1"

check "SOAPNoteDraft schema defined" \
    "grep -c 'class SOAPNoteDraft' src/schemas/integration.py" \
    "1"

check "ConversionMetadata schema defined" \
    "grep -c 'class ConversionMetadata' src/schemas/integration.py" \
    "1"

check "Australian terminology validator present" \
    "grep -c 'validate_australian_terminology' src/schemas/integration.py" \
    "[1-9]"

echo ""
echo "=== 6. CONVERTER SERVICE VALIDATION ==="
echo ""

check "OSCEToEMRConverter class defined" \
    "grep -c 'class OSCEToEMRConverter' src/services/integration/osce_to_emr_converter.py" \
    "1"

check "Main convert method exists" \
    "grep -c 'async def convert' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "Claude API extraction method exists" \
    "grep -c '_extract_clinical_data_with_claude' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "Extraction prompt builder exists" \
    "grep -c '_build_extraction_prompt' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "PHI anonymization function exists" \
    "grep -c 'def _anonymize_phi' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "Fallback conversion exists" \
    "grep -c '_fallback_conversion' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "Claude model specified (claude-3-5-sonnet)" \
    "grep -c 'claude-3-5-sonnet' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

check "Australian context in prompt" \
    "grep -c 'eTG\|AMH\|PBS\|MBS' src/services/integration/osce_to_emr_converter.py" \
    "[1-9]"

echo ""
echo "=== 7. API ENDPOINT VALIDATION ==="
echo ""

check "API router defined" \
    "grep -c 'router = APIRouter' src/api/v1/integration/converter.py" \
    "1"

check "POST /osce-to-emr endpoint defined" \
    "grep -c '@router.post' src/api/v1/integration/converter.py" \
    "[1-9]"

check "GET /conversion-stats endpoint defined" \
    "grep -c '@router.get' src/api/v1/integration/converter.py" \
    "[1-9]"

check "User authentication required" \
    "grep -c 'get_current_user' src/api/v1/integration/converter.py" \
    "[2-9]"

check "Database session dependency" \
    "grep -c 'get_db' src/api/v1/integration/converter.py" \
    "[2-9]"

check "Error handling (HTTPException)" \
    "grep -c 'HTTPException' src/api/v1/integration/converter.py" \
    "[3-9]"

echo ""
echo "=== 8. TEST SUITE VALIDATION ==="
echo ""

check "Test class defined" \
    "grep -c 'class TestOSCEToEMRConverter' tests/test_integration/test_osce_to_emr_converter.py" \
    "1"

check "Chest pain test scenario" \
    "grep -c 'test_chest_pain_conversion' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "Headache test scenario" \
    "grep -c 'test_headache_conversion' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "Incomplete OSCE test" \
    "grep -c 'test_incomplete_osce' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "Australian terminology test" \
    "grep -c 'test_australian_terminology' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "Performance test (<500ms)" \
    "grep -c 'test_performance' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "Vault integration test" \
    "grep -c 'test_vault_integration' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "Claude API failure test" \
    "grep -c 'test_claude_api_failure' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "User authorization test" \
    "grep -c 'test_user_authorization' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

check "Breaking bad news test" \
    "grep -c 'test_breaking_bad_news' tests/test_integration/test_osce_to_emr_converter.py" \
    "[1-9]"

test_count=$(grep -c 'async def test_' tests/test_integration/test_osce_to_emr_converter.py || echo 0)
echo "Total test methods: $test_count (expected: 12)"

if [[ $test_count -ge 12 ]]; then
    echo -e "${GREEN}Test count PASS${NC} (≥12 scenarios)"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}Test count FAIL${NC} (expected ≥12, got $test_count)"
    ((CHECKS_FAILED++))
fi

echo ""
echo "=== 9. DOCUMENTATION VALIDATION ==="
echo ""

check "Implementation summary exists" \
    "ls OSCE_EMR_CONVERTER_IMPLEMENTATION_SUMMARY.md" \
    "OSCE_EMR_CONVERTER_IMPLEMENTATION_SUMMARY.md"

check "Summary has success criteria section" \
    "grep -c 'Success Criteria' OSCE_EMR_CONVERTER_IMPLEMENTATION_SUMMARY.md" \
    "[1-9]"

check "Summary has validation checklist" \
    "grep -c 'Validation Checklist' OSCE_EMR_CONVERTER_IMPLEMENTATION_SUMMARY.md" \
    "[1-9]"

check "Summary has API testing examples" \
    "grep -c 'API Testing Examples' OSCE_EMR_CONVERTER_IMPLEMENTATION_SUMMARY.md" \
    "[1-9]"

echo ""
echo "=== 10. PYTHON SYNTAX VALIDATION ==="
echo ""

if command -v python3 &> /dev/null; then
    if python3 -m py_compile src/schemas/integration.py 2>&1; then
        echo -e "Schemas syntax: ${GREEN}PASS${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "Schemas syntax: ${RED}FAIL${NC}"
        ((CHECKS_FAILED++))
    fi

    if python3 -m py_compile src/services/integration/osce_to_emr_converter.py 2>&1; then
        echo -e "Converter service syntax: ${GREEN}PASS${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "Converter service syntax: ${RED}FAIL${NC}"
        ((CHECKS_FAILED++))
    fi

    if python3 -m py_compile src/api/v1/integration/converter.py 2>&1; then
        echo -e "API endpoint syntax: ${GREEN}PASS${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "API endpoint syntax: ${RED}FAIL${NC}"
        ((CHECKS_FAILED++))
    fi

    if python3 -m py_compile tests/test_integration/test_osce_to_emr_converter.py 2>&1; then
        echo -e "Test suite syntax: ${GREEN}PASS${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "Test suite syntax: ${RED}FAIL${NC}"
        ((CHECKS_FAILED++))
    fi
else
    echo -e "${YELLOW}Python3 not available - skipping syntax checks${NC}"
fi

echo ""
echo "=============================================="
echo "VERIFICATION SUMMARY"
echo "=============================================="
echo ""
echo -e "Checks passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Checks failed: ${RED}$CHECKS_FAILED${NC}"
echo ""

total_checks=$((CHECKS_PASSED + CHECKS_FAILED))
pass_rate=$((CHECKS_PASSED * 100 / total_checks))

echo "Pass rate: $pass_rate% ($CHECKS_PASSED/$total_checks)"
echo ""

if [[ $CHECKS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All checks PASSED - Implementation ready for testing${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start PostgreSQL database"
    echo "2. Run migration: alembic upgrade head"
    echo "3. Set Vault secret: vault kv put secret/irStudy/claude value=<api-key>"
    echo "4. Run tests: pytest tests/test_integration/test_osce_to_emr_converter.py -v"
    echo "5. Start backend: uvicorn main:app --reload"
    echo "6. Test API endpoint: curl -X POST http://localhost:8001/api/v1/integration/osce-to-emr"
    exit 0
else
    echo -e "${RED}✗ Some checks FAILED - Review errors above${NC}"
    exit 1
fi
