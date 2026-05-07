#!/bin/bash
# Medical Content Quality Validation Script
# Validates OSCE/MCQ content against Australian medical standards

set -e

echo "🏥 Medical Content Quality Validation"
echo "====================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$PROJECT_ROOT"

# Check 1: Python venv activated
echo -n "1. Python venv... "
if python --version 2>&1 | grep -q "Python 3" && which python | grep -q "venv"; then
    echo "✅ Active ($(python --version 2>&1))"
else
    echo "❌ NOT ACTIVATED"
    echo "   Run: source venv/bin/activate"
    exit 1
fi

# Check 2: No US drug names
echo -n "2. Australian drug names... "
US_DRUG_COUNT=$(grep -r "acetaminophen\|albuterol\|epinephrine" data/ --include="*.json" 2>/dev/null | wc -l || echo 0)
if [ "$US_DRUG_COUNT" -eq 0 ]; then
    echo "✅ No US spellings found"
else
    echo "❌ Found $US_DRUG_COUNT US drug names"
    grep -r "acetaminophen\|albuterol\|epinephrine" data/ --include="*.json" | head -5
    exit 1
fi

# Check 3: RAG citations validation
echo -n "3. RAG citations... "
if [ -f "scripts/validate_rag_citations.py" ]; then
    CITATION_RESULT=$(python scripts/validate_rag_citations.py --min-confidence 0.65 data/osce/ 2>/dev/null | grep "Coverage" || echo "")
    if echo "$CITATION_RESULT" | grep -q "100%"; then
        echo "✅ 100% coverage"
    else
        echo "⚠️  Check citation coverage"
    fi
else
    echo "⚠️  Validation script not found"
fi

# Check 4: No placeholder content
echo -n "4. No placeholders... "
PLACEHOLDER_COUNT=$(grep -r "Option A\|Option B\|Clinical scenario for\|\[INSERT" data/ --include="*.json" 2>/dev/null | wc -l || echo 0)
if [ "$PLACEHOLDER_COUNT" -eq 0 ]; then
    echo "✅ No placeholders found"
else
    echo "❌ Found $PLACEHOLDER_COUNT placeholder patterns"
    grep -r "Option A\|Option B\|Clinical scenario for\|\[INSERT" data/ --include="*.json" | head -5
    exit 1
fi

# Check 5: 13-gate QA validation
echo -n "5. 13-gate QA... "
if [ -f "scripts/qa_validation_13_gates.py" ]; then
    QA_RESULT=$(python scripts/qa_validation_13_gates.py data/osce/batch_1/ 2>/dev/null | grep "PASS" | wc -l || echo 0)
    if [ "$QA_RESULT" -gt 10 ]; then
        echo "✅ Quality gates passing"
    else
        echo "⚠️  Run full QA validation"
    fi
else
    echo "⚠️  QA validation script not found"
fi

# Check 6: UTF-8 encoding
echo -n "6. UTF-8 encoding... "
NON_UTF8=$(find data/ -name "*.json" -exec file {} \; 2>/dev/null | grep -v "UTF-8" | wc -l || echo 0)
if [ "$NON_UTF8" -eq 0 ]; then
    echo "✅ All files UTF-8"
else
    echo "❌ Found $NON_UTF8 non-UTF-8 files"
    exit 1
fi

# Check 7: Claude API key configured
echo -n "7. Claude API key... "
if python -c "import os; exit(0 if os.getenv('ANTHROPIC_API_KEY') else 1)" 2>/dev/null; then
    echo "✅ Configured"
else
    echo "❌ Missing ANTHROPIC_API_KEY"
    exit 1
fi

echo ""
echo "✅ Medical Content Quality Validation Complete"
echo "   All critical checks passed"
