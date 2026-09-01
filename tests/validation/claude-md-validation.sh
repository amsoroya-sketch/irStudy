#!/bin/bash

# Phase 1 Validation: .claude/CLAUDE.md for irStudy
# Tests Python/FastAPI, TypeScript/React, medical content, and Ponytail patterns

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing .claude/CLAUDE.md for irStudy..."
echo ""

cd /home/dev/Development/irStudy || exit 1

# Test 1: .claude/CLAUDE.md exists
test_file_exists() {
  if [ -f .claude/CLAUDE.md ]; then
    echo -e "${GREEN}✅ Test 1 PASS: .claude/CLAUDE.md exists${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 1 FAIL: .claude/CLAUDE.md missing${NC}"
    return 1
  fi
}

# Test 2: Python/FastAPI patterns documented
test_python_patterns() {
  if grep -q "FastAPI\|Python.*pattern\|SQLAlchemy\|Alembic" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Test 2 PASS: Python/FastAPI patterns documented${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 2 FAIL: Python/FastAPI patterns missing${NC}"
    return 1
  fi
}

# Test 3: TypeScript/React patterns documented
test_typescript_patterns() {
  if grep -q "TypeScript\|React.*pattern\|useState\|useEffect" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Test 3 PASS: TypeScript/React patterns documented${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 3 FAIL: TypeScript/React patterns missing${NC}"
    return 1
  fi
}

# Test 4: Medical content validation patterns documented
test_medical_validation() {
  if grep -q "RAG.*Content\|medical content\|qdrant_point_id\|citation" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Test 4 PASS: Medical content validation patterns documented${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 4 FAIL: Medical content validation patterns missing${NC}"
    return 1
  fi
}

# Test 5: Quality gates referenced
test_quality_gates() {
  if grep -q "pytest\|npm test\|flutter analyze\|Quality Gate" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Test 5 PASS: Quality gates referenced${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 5 FAIL: Quality gates missing${NC}"
    return 1
  fi
}

# Test 6: Cross-system coordination documented
test_cross_system() {
  if grep -q "Cross-System\|EMR.*OSCE\|Shared Infrastructure" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Test 6 PASS: Cross-system coordination documented${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 6 FAIL: Cross-system coordination missing${NC}"
    return 1
  fi
}

# Test 7: Ponytail/Code Reuse section present
test_ponytail_section() {
  if grep -q "Ponytail\|Code Reuse.*Strategy\|DISCOVERY" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Test 7 PASS: Ponytail section present${NC}"
    return 0
  else
    echo -e "${RED}❌ Test 7 FAIL: Ponytail section missing${NC}"
    return 1
  fi
}

# Run tests
FAILED=0

test_file_exists || FAILED=1
test_python_patterns || FAILED=1
test_typescript_patterns || FAILED=1
test_medical_validation || FAILED=1
test_quality_gates || FAILED=1
test_cross_system || FAILED=1
test_ponytail_section || FAILED=1

echo ""
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}🎉 All .claude/CLAUDE.md tests PASSED (7/7)${NC}"
  exit 0
else
  echo -e "${RED}❌ Some tests FAILED${NC}"
  exit 1
fi
