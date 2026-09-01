#!/bin/bash

# Phase 3 Validation: GitHub Actions CI/CD workflows for irStudy
# Tests Python, TypeScript, and security scan workflows

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing GitHub Actions workflows..."
echo ""

cd /home/dev/Development/irStudy || exit 1

# Test 1: python-quality-gates.yml exists
test_python_workflow() {
  if [ -f .github/workflows/python-quality-gates.yml ]; then
    echo -e "${GREEN}✅ Test 1 PASS: python-quality-gates.yml exists${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 1 FAIL: python-quality-gates.yml missing${NC}"
    return 1
  fi
}

# Test 2: Python workflow has pytest and pylint
test_python_workflow_content() {
  if grep -q "pytest.*--cov" .github/workflows/python-quality-gates.yml && \
     grep -q "pylint" .github/workflows/python-quality-gates.yml; then
    echo -e "${GREEN}✅ Test 2 PASS: Python workflow has pytest + pylint${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 2 FAIL: Python workflow missing pytest or pylint${NC}"
    return 1
  fi
}

# Test 3: typescript-quality-gates.yml exists
test_typescript_workflow() {
  if [ -f .github/workflows/typescript-quality-gates.yml ]; then
    echo -e "${GREEN}✅ Test 3 PASS: typescript-quality-gates.yml exists${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 3 FAIL: typescript-quality-gates.yml missing${NC}"
    return 1
  fi
}

# Test 4: TypeScript workflow has tsc and npm test
test_typescript_workflow_content() {
  if grep -q "tsc --noEmit" .github/workflows/typescript-quality-gates.yml && \
     grep -q "npm test" .github/workflows/typescript-quality-gates.yml; then
    echo -e "${GREEN}✅ Test 4 PASS: TypeScript workflow has tsc + npm test${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 4 FAIL: TypeScript workflow missing tsc or npm test${NC}"
    return 1
  fi
}

# Test 5: security-scan.yml exists
test_security_workflow() {
  if [ -f .github/workflows/security-scan.yml ]; then
    echo -e "${GREEN}✅ Test 5 PASS: security-scan.yml exists${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 5 FAIL: security-scan.yml missing${NC}"
    return 1
  fi
}

# Test 6: Security workflow scans for API keys and credentials
test_security_workflow_content() {
  if grep -q "sk-ant-" .github/workflows/security-scan.yml && \
     grep -q "api_key" .github/workflows/security-scan.yml && \
     grep -q "dbPath\|dbKey" .github/workflows/security-scan.yml; then
    echo -e "${GREEN}✅ Test 6 PASS: Security workflow scans for API keys + credentials${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 6 FAIL: Security workflow missing key scans${NC}"
    return 1
  fi
}

# Run tests
FAILED=0

test_python_workflow || FAILED=1
test_python_workflow_content || FAILED=1
test_typescript_workflow || FAILED=1
test_typescript_workflow_content || FAILED=1
test_security_workflow || FAILED=1
test_security_workflow_content || FAILED=1

echo ""
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}🎉 All GitHub Actions workflows tests PASSED (6/6)${NC}"
  exit 0
else
  echo -e "${RED}❌ Some tests FAILED${NC}"
  exit 1
fi
