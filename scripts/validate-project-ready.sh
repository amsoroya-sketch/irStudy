#!/bin/bash

# Ralph Validation Script for irStudy
# Validates project readiness before Ralph PRD execution

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage: ./scripts/validate-project-ready.sh [PRD-FILE.md]

if [ -z "$1" ]; then
  echo -e "${RED}Usage: $0 <PRD-FILE.md>${NC}"
  echo "Example: $0 PRD-OSCE-001-SCENARIO-ENGINE.md"
  exit 1
fi

PRD_FILE="$1"

echo -e "${YELLOW}Validating irStudy project readiness for Ralph execution...${NC}"
echo ""

FAILED=0

# ============================================
# 1. Check PROJECT_CONSTRAINTS.md
# ============================================

echo -e "${YELLOW}[1/5] Checking PROJECT_CONSTRAINTS.md...${NC}"

if [ -f "PROJECT_CONSTRAINTS.md" ]; then
  # Check if file is comprehensive (>500 lines)
  line_count=$(wc -l < PROJECT_CONSTRAINTS.md)
  if [ "$line_count" -gt 500 ]; then
    echo -e "${GREEN}✅ PROJECT_CONSTRAINTS.md exists (${line_count} lines)${NC}"
  else
    echo -e "${RED}❌ PROJECT_CONSTRAINTS.md too small (${line_count} lines)${NC}"
    FAILED=1
  fi

  # Check for Ponytail section
  if grep -q "Ponytail\|Code Reuse.*Strategy\|## 0 - DISCOVERY" PROJECT_CONSTRAINTS.md; then
    echo -e "${GREEN}✅ Ponytail section present${NC}"
  else
    echo -e "${RED}❌ Ponytail section missing${NC}"
    FAILED=1
  fi
else
  echo -e "${RED}❌ PROJECT_CONSTRAINTS.md not found${NC}"
  FAILED=1
fi

# ============================================
# 2. Check .claude/CLAUDE.md
# ============================================

echo ""
echo -e "${YELLOW}[2/5] Checking .claude/CLAUDE.md...${NC}"

if [ -f ".claude/CLAUDE.md" ]; then
  echo -e "${GREEN}✅ .claude/CLAUDE.md exists${NC}"

  # Check for project-specific patterns
  if grep -q "FastAPI\|Python.*pattern\|TypeScript\|React" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Project-specific patterns documented${NC}"
  else
    echo -e "${RED}❌ Project-specific patterns missing${NC}"
    FAILED=1
  fi

  # Check for Ponytail section
  if grep -q "Ponytail\|Code Reuse\|DISCOVERY" .claude/CLAUDE.md; then
    echo -e "${GREEN}✅ Ponytail section present${NC}"
  else
    echo -e "${RED}❌ Ponytail section missing${NC}"
    FAILED=1
  fi
else
  echo -e "${RED}❌ .claude/CLAUDE.md not found${NC}"
  FAILED=1
fi

# ============================================
# 3. Check PRD Structure (if file exists)
# ============================================

echo ""
echo -e "${YELLOW}[3/5] Checking PRD structure...${NC}"

if [ -f "$PRD_FILE" ]; then
  echo -e "${GREEN}✅ PRD file found: $PRD_FILE${NC}"

  # Check for Section 0 (Discovery)
  if grep -q "^## 0 - DISCOVERY" "$PRD_FILE"; then
    echo -e "${GREEN}✅ Section 0 (Discovery) present${NC}"
  else
    echo -e "${RED}❌ Section 0 (Discovery) missing - Ralph PRDs MUST have Section 0${NC}"
    FAILED=1
  fi

  # Check for T-RALPH structure
  if grep -q "^## T - TESTS\|^## R - REQUEST\|^## A - ARCHITECTURE" "$PRD_FILE"; then
    echo -e "${GREEN}✅ T-RALPH structure present${NC}"
  else
    echo -e "${YELLOW}⚠️  T-RALPH structure not detected (optional for some PRDs)${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  PRD file not found: $PRD_FILE (will be created by Ralph)${NC}"
fi

# ============================================
# 4. Check Quality Gates Availability
# ============================================

echo ""
echo -e "${YELLOW}[4/5] Checking quality gates...${NC}"

# Check Python tools
if command -v pytest &> /dev/null; then
  echo -e "${GREEN}✅ pytest available${NC}"
else
  echo -e "${RED}❌ pytest not found (run: pip install pytest)${NC}"
  FAILED=1
fi

if command -v pylint &> /dev/null; then
  echo -e "${GREEN}✅ pylint available${NC}"
else
  echo -e "${RED}❌ pylint not found (run: pip install pylint)${NC}"
  FAILED=1
fi

# Check TypeScript tools (if frontend exists)
if [ -d "frontend" ]; then
  if [ -f "frontend/node_modules/.bin/tsc" ] || command -v tsc &> /dev/null; then
    echo -e "${GREEN}✅ TypeScript compiler available${NC}"
  else
    echo -e "${RED}❌ TypeScript compiler not found (run: cd frontend && npm install)${NC}"
    FAILED=1
  fi
fi

# ============================================
# 5. Check Git Repository
# ============================================

echo ""
echo -e "${YELLOW}[5/5] Checking Git configuration...${NC}"

if [ -d ".git" ]; then
  echo -e "${GREEN}✅ Git repository initialized${NC}"

  # Check for pre-commit hook
  if [ -f ".git/hooks/pre-commit" ] && [ -x ".git/hooks/pre-commit" ]; then
    echo -e "${GREEN}✅ Pre-commit hook installed${NC}"
  else
    echo -e "${YELLOW}⚠️  Pre-commit hook not installed (recommended)${NC}"
  fi
else
  echo -e "${RED}❌ Git repository not initialized${NC}"
  FAILED=1
fi

# ============================================
# Summary
# ============================================

echo ""
echo "======================================"
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✅ Project ready for Ralph execution!${NC}"
  echo "======================================"
  echo ""
  echo "Next steps:"
  echo "1. cd /home/dev/Development/ralph-dashboard"
  echo "2. ./scripts/ralph_loop.sh --calls 50 --prompt /home/dev/Development/irStudy/$PRD_FILE"
  exit 0
else
  echo -e "${RED}❌ Project NOT ready for Ralph execution${NC}"
  echo "======================================"
  echo ""
  echo "Fix the issues above before running Ralph."
  exit 1
fi
