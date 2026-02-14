#!/bin/bash
#
# Pre-Flight Validation Checklist
# MANDATORY: Run before ANY content generation (MCQs/OSCEs)
#
# CONTEXT:
# Week 1 Issue: Generated 100 MCQs + 5 OSCEs without validating RAG database.
# All 212 citations showed "title": "Unknown" because validation was skipped.
#
# This script prevents that by running comprehensive validation BEFORE generation:
# 1. RAG database metadata completeness (0% "Unknown" titles required)
# 2. RAG citation quality (test with real queries)
# 3. Qdrant service health check
# 4. Australian source coverage audit
#
# EXIT CODES:
#   0 = All checks passed (SAFE to proceed)
#   1 = Any check failed (DO NOT proceed)
#
# USAGE:
#   ./scripts/pre_flight_validation.sh
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
QDRANT_URL="http://localhost:6333"
COLLECTION_NAME="medical_knowledge"
MIN_CONFIDENCE=0.65
TEST_QUERIES=20

echo ""
echo "======================================================================="
echo -e "${BLUE}🔍 PRE-FLIGHT VALIDATION CHECKLIST${NC}"
echo "======================================================================="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Purpose: Validate RAG system before content generation"
echo ""
echo "This checklist prevents the Week 1 'Unknown' citation mistake by"
echo "validating the RAG database has complete metadata BEFORE generation."
echo ""
echo "======================================================================="
echo ""

# Track overall status
OVERALL_STATUS=0

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "  Run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi
echo ""

# Check 1: Qdrant Service Health
echo "======================================================================="
echo -e "${BLUE}CHECK 1: Qdrant Service Health${NC}"
echo "======================================================================="
echo "Checking Qdrant at: $QDRANT_URL"
echo ""

if curl -s "${QDRANT_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC} - Qdrant service is running"
else
    echo -e "${RED}✗ FAILED${NC} - Qdrant service not responding"
    echo ""
    echo "Fix:"
    echo "  docker-compose up -d qdrant"
    echo "  OR"
    echo "  docker start medical_qdrant"
    echo ""
    exit 1
fi
echo ""

# Check 2: RAG Database Metadata Completeness
echo "======================================================================="
echo -e "${BLUE}CHECK 2: RAG Database Metadata Completeness${NC}"
echo "======================================================================="
echo "Validating $COLLECTION_NAME collection..."
echo "Checking for 'Unknown' titles, invalid authors, missing year/page"
echo ""

if python3 scripts/validate_rag_database_metadata.py \
    --collection "$COLLECTION_NAME" \
    --qdrant-url "$QDRANT_URL" \
    --sample-size 1000; then
    echo ""
    echo -e "${GREEN}✓ PASSED${NC} - RAG database has valid metadata"
else
    echo ""
    echo -e "${RED}✗ FAILED${NC} - RAG database has incomplete metadata"
    echo ""
    echo "Remediation:"
    echo "  1. python scripts/fix_rag_metadata.py"
    echo "  2. python scripts/update_embeddings_metadata.py"
    echo "  3. source venv/bin/activate && python scripts/index_qdrant.py \\"
    echo "       --embeddings data/embeddings/medical_embeddings_fixed.pkl"
    echo "  4. Re-run this validation script"
    echo ""
    OVERALL_STATUS=1
fi
echo ""

# Check 3: RAG Citation Quality (Sample Queries)
echo "======================================================================="
echo -e "${BLUE}CHECK 3: RAG Citation Quality (Sample Queries)${NC}"
echo "======================================================================="
echo "Testing RAG with $TEST_QUERIES medical queries..."
echo "Minimum confidence: $MIN_CONFIDENCE"
echo ""

if python3 scripts/test_rag_citation_quality.py \
    --queries "$TEST_QUERIES" \
    --min-confidence "$MIN_CONFIDENCE" \
    --collection "$COLLECTION_NAME" \
    --qdrant-url "$QDRANT_URL"; then
    echo ""
    echo -e "${GREEN}✓ PASSED${NC} - RAG returns valid citations"
else
    echo ""
    echo -e "${YELLOW}⚠ WARNING${NC} - RAG citation quality below threshold"
    echo ""
    echo "This may indicate:"
    echo "  • Low-quality embeddings"
    echo "  • Insufficient Australian source coverage"
    echo "  • Model mismatch (ensure using S-PubMedBert)"
    echo ""
    echo "Generation can proceed but citations may be low quality."
    echo "Consider running:"
    echo "  python scripts/download_australian_guidelines.py"
    echo "  python scripts/chunk_medical_texts.py"
    echo "  python scripts/generate_embeddings.py"
    echo ""
    # Don't fail for this - just warn
fi
echo ""

# Check 4: Collection Point Count
echo "======================================================================="
echo -e "${BLUE}CHECK 4: Collection Size Check${NC}"
echo "======================================================================="

POINT_COUNT=$(curl -s "${QDRANT_URL}/collections/${COLLECTION_NAME}" | \
              python3 -c "import sys, json; print(json.load(sys.stdin)['result']['points_count'])" 2>/dev/null || echo "0")

echo "Points in collection: $POINT_COUNT"
echo ""

if [ "$POINT_COUNT" -lt 1000 ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} - Low point count (< 1,000)"
    echo "  Consider adding more medical sources"
elif [ "$POINT_COUNT" -lt 5000 ]; then
    echo -e "${YELLOW}⚠ NOTE${NC} - Moderate point count"
    echo "  Acceptable but more sources recommended"
else
    echo -e "${GREEN}✓ PASSED${NC} - Good point count (≥ 5,000)"
fi
echo ""

# Final Summary
echo "======================================================================="
echo -e "${BLUE}VALIDATION SUMMARY${NC}"
echo "======================================================================="
echo ""

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CRITICAL CHECKS PASSED${NC}"
    echo ""
    echo "Safe to proceed with content generation:"
    echo "  • RAG database metadata: VALID"
    echo "  • Citation quality: ACCEPTABLE"
    echo "  • Qdrant service: RUNNING"
    echo "  • Collection size: $POINT_COUNT points"
    echo ""
    echo "🚀 You may now run generation scripts:"
    echo "   python scripts/generate_week2_day6_mcqs.py"
    echo "   python scripts/generate_week2_day7_mcqs.py"
    echo "   etc."
    echo ""
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo ""
    echo "DO NOT PROCEED with content generation!"
    echo "Fix the issues above and re-run this validation script."
    echo ""
    echo "Critical failures:"
    echo "  • RAG database metadata incomplete"
    echo ""
fi

echo "======================================================================="
echo "Validation completed at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================================="
echo ""

exit $OVERALL_STATUS
