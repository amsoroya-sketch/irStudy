#!/bin/bash

# Phase 5 Validation: Ralph validation script for irStudy
# Tests Ralph validation script installation and checks

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing Ralph validation script..."
echo ""

cd /home/dev/Development/irStudy || exit 1

# Test 1: Script exists
test_script_exists() {
  if [ -f scripts/validate-project-ready.sh ]; then
    echo -e "${GREEN}✅ Test 1 PASS: Ralph validation script exists${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 1 FAIL: Ralph validation script missing${NC}"
    return 1
  fi
}

# Test 2: Script is executable
test_script_executable() {
  if [ -x scripts/validate-project-ready.sh ]; then
    echo -e "${GREEN}✅ Test 2 PASS: Ralph validation script is executable${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 2 FAIL: Ralph validation script not executable${NC}"
    return 1
  fi
}

# Test 3: Script checks PROJECT_CONSTRAINTS.md
test_checks_constraints() {
  if grep -q "PROJECT_CONSTRAINTS.md" scripts/validate-project-ready.sh; then
    echo -e "${GREEN}✅ Test 3 PASS: Script checks PROJECT_CONSTRAINTS.md${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 3 FAIL: Script doesn't check PROJECT_CONSTRAINTS.md${NC}"
    return 1
  fi
}

# Test 4: Script checks .claude/CLAUDE.md
test_checks_claude_md() {
  if grep -q ".claude/CLAUDE.md" scripts/validate-project-ready.sh; then
    echo -e "${GREEN}✅ Test 4 PASS: Script checks .claude/CLAUDE.md${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 4 FAIL: Script doesn't check .claude/CLAUDE.md${NC}"
    return 1
  fi
}

# Test 5: Script checks for Section 0 in PRDs
test_checks_section_0() {
  if grep -q "Section 0.*DISCOVERY\|## 0 - DISCOVERY" scripts/validate-project-ready.sh; then
    echo -e "${GREEN}✅ Test 5 PASS: Script checks for Section 0${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 5 FAIL: Script doesn't check for Section 0${NC}"
    return 1
  fi
}

# Run tests
FAILED=0

test_script_exists || FAILED=1
test_script_executable || FAILED=1
test_checks_constraints || FAILED=1
test_checks_claude_md || FAILED=1
test_checks_section_0 || FAILED=1

echo ""
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}🎉 All Ralph validation script tests PASSED (5/5)${NC}"
  exit 0
else
  echo -e "${RED}❌ Some tests FAILED${NC}"
  exit 1
fi
