#!/bin/bash

# Phase 4 Validation: Pre-commit hook for irStudy
# Tests pre-commit hook installation and quality gate checks

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing pre-commit hook..."
echo ""

cd /home/dev/Development/irStudy || exit 1

# Test 1: Pre-commit hook exists
test_hook_exists() {
  if [ -f .git/hooks/pre-commit ]; then
    echo -e "${GREEN}✅ Test 1 PASS: Pre-commit hook exists${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 1 FAIL: Pre-commit hook missing${NC}"
    return 1
  fi
}

# Test 2: Hook is executable
test_hook_executable() {
  if [ -x .git/hooks/pre-commit ]; then
    echo -e "${GREEN}✅ Test 2 PASS: Pre-commit hook is executable${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 2 FAIL: Pre-commit hook not executable${NC}"
    return 1
  fi
}

# Test 3: Hook contains Python quality gates
test_python_gates() {
  if grep -q "pytest\|pylint\|coverage" .git/hooks/pre-commit; then
    echo -e "${GREEN}✅ Test 3 PASS: Python quality gates present${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 3 FAIL: Python quality gates missing${NC}"
    return 1
  fi
}

# Test 4: Hook contains TypeScript quality gates
test_typescript_gates() {
  if grep -q "tsc --noEmit\|npm run lint\|npm test" .git/hooks/pre-commit; then
    echo -e "${GREEN}✅ Test 4 PASS: TypeScript quality gates present${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 4 FAIL: TypeScript quality gates missing${NC}"
    return 1
  fi
}

# Test 5: Hook contains security scans
test_security_scans() {
  if grep -q "sk-ant-\|dbPath:\|PHI" .git/hooks/pre-commit; then
    echo -e "${GREEN}✅ Test 5 PASS: Security scans present${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 5 FAIL: Security scans missing${NC}"
    return 1
  fi
}

# Run tests
FAILED=0

test_hook_exists || FAILED=1
test_hook_executable || FAILED=1
test_python_gates || FAILED=1
test_typescript_gates || FAILED=1
test_security_scans || FAILED=1

echo ""
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}🎉 All pre-commit hook tests PASSED (5/5)${NC}"
  exit 0
else
  echo -e "${RED}❌ Some tests FAILED${NC}"
  exit 1
fi
