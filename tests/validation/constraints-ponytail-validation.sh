#!/bin/bash

# Phase 2 Validation: PROJECT_CONSTRAINTS.md Ponytail section for irStudy
# Tests Ponytail integration, Section 0 references, discovery commands

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing PROJECT_CONSTRAINTS.md Ponytail section..."
echo ""

cd /home/dev/Development/irStudy || exit 1

# Test 1: PROJECT_CONSTRAINTS.md exists and is comprehensive
test_file_exists() {
  if [ -f PROJECT_CONSTRAINTS.md ] && [ $(wc -l < PROJECT_CONSTRAINTS.md) -gt 500 ]; then
    echo -e "${GREEN}✅ Test 1 PASS: PROJECT_CONSTRAINTS.md exists and is comprehensive${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 1 FAIL: PROJECT_CONSTRAINTS.md missing or too small${NC}"
    return 1
  fi
}

# Test 2: Contains Ponytail section
test_ponytail_section() {
  if grep -q "Ponytail.*Strategy\|Code Reuse.*Strategy\|DISCOVERY.*CODE REUSE" PROJECT_CONSTRAINTS.md; then
    echo -e "${GREEN}✅ Test 2 PASS: Ponytail section present${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 2 FAIL: Ponytail section missing${NC}"
    return 1
  fi
}

# Test 3: Ponytail section references Section 0
test_section_0_reference() {
  if grep -q "Section 0.*DISCOVERY\|## 0 - DISCOVERY" PROJECT_CONSTRAINTS.md; then
    echo -e "${GREEN}✅ Test 3 PASS: Section 0 (Discovery) referenced${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 3 FAIL: Section 0 not referenced${NC}"
    return 1
  fi
}

# Test 4: Contains discovery command examples (Python/TypeScript/RAG)
test_discovery_commands() {
  if grep -q "find.*routers\|grep -r.*backend\|curl.*qdrant" PROJECT_CONSTRAINTS.md; then
    echo -e "${GREEN}✅ Test 4 PASS: Discovery commands present${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 4 FAIL: Discovery commands missing${NC}"
    return 1
  fi
}

# Run tests
FAILED=0

test_file_exists || FAILED=1
test_ponytail_section || FAILED=1
test_section_0_reference || FAILED=1
test_discovery_commands || FAILED=1

echo ""
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}🎉 All PROJECT_CONSTRAINTS.md Ponytail tests PASSED (4/4)${NC}"
  exit 0
else
  echo -e "${RED}❌ Some tests FAILED${NC}"
  exit 1
fi
