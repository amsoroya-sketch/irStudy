#!/bin/bash
# Content Substance Validation Script
# Detects placeholder content in MCQs, OSCEs, and Study Cards
# Exit code 0 = PASS (no placeholders), Exit code 2 = FAIL (placeholders detected)
#
# Usage: ./validate_content_substance.sh <file.json>
# Pre-commit hook: Automatically runs on git commit for MCQ/OSCE files
#
# Reference: constraints/12-content-generation-requirements.md

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# File to validate
FILE="$1"

if [ -z "$FILE" ]; then
    echo -e "${RED}❌ ERROR: No file specified${NC}"
    echo "Usage: $0 <file.json>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo -e "${RED}❌ ERROR: File not found: $FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Validating content substance: $FILE${NC}"
echo ""

# Initialize counters
PLACEHOLDER_COUNT=0
SHORT_SCENARIO_COUNT=0
SHORT_EXPLANATION_COUNT=0
NO_DEMOGRAPHICS_COUNT=0
NO_AUSTRALIAN_CONTEXT_COUNT=0

# Check for placeholder patterns
echo "Checking for placeholder patterns..."

# Pattern 1: "Clinical scenario for..."
if grep -q "Clinical scenario for" "$FILE"; then
    COUNT=$(grep -c "Clinical scenario for" "$FILE")
    echo -e "${RED}  ❌ Found $COUNT instances of 'Clinical scenario for...'${NC}"
    PLACEHOLDER_COUNT=$((PLACEHOLDER_COUNT + COUNT))
fi

# Pattern 2: "Question stem about..."
if grep -q "Question stem about" "$FILE"; then
    COUNT=$(grep -c "Question stem about" "$FILE")
    echo -e "${RED}  ❌ Found $COUNT instances of 'Question stem about...'${NC}"
    PLACEHOLDER_COUNT=$((PLACEHOLDER_COUNT + COUNT))
fi

# Pattern 3: Generic "Option A/B/C/D"
if grep -qE '"[A-D]":\s*"Option [A-D]"' "$FILE"; then
    COUNT=$(grep -cE '"[A-D]":\s*"Option [A-D]"' "$FILE")
    echo -e "${RED}  ❌ Found $COUNT instances of generic 'Option A/B/C/D'${NC}"
    PLACEHOLDER_COUNT=$((PLACEHOLDER_COUNT + COUNT))
fi

# Pattern 4: "Explanation for..."
if grep -q "Explanation for" "$FILE"; then
    COUNT=$(grep -c "Explanation for" "$FILE")
    echo -e "${RED}  ❌ Found $COUNT instances of 'Explanation for...'${NC}"
    PLACEHOLDER_COUNT=$((PLACEHOLDER_COUNT + COUNT))
fi

# Pattern 5: "{topic}" or "{condition}" placeholders
if grep -qE '\{topic\}|\{condition\}|\{disease\}|\{medication\}' "$FILE"; then
    COUNT=$(grep -cE '\{topic\}|\{condition\}|\{disease\}|\{medication\}' "$FILE")
    echo -e "${RED}  ❌ Found $COUNT instances of unresolved placeholders (e.g., {topic})${NC}"
    PLACEHOLDER_COUNT=$((PLACEHOLDER_COUNT + COUNT))
fi

if [ $PLACEHOLDER_COUNT -eq 0 ]; then
    echo -e "${GREEN}  ✅ No placeholder patterns detected${NC}"
fi

echo ""

# Check for content substance (minimum lengths)
echo "Checking content substance (minimum lengths)..."

# Use Python to check JSON content lengths
python3 << EOF
import json
import sys

try:
    with open("$FILE", "r", encoding="utf-8") as f:
        data = json.load(f)

    short_scenarios = 0
    short_explanations = 0
    no_demographics = 0
    no_australian = 0

    # Handle both single item and array of items
    items = data if isinstance(data, list) else [data]

    for i, item in enumerate(items):
        # Check scenarios (MCQs/OSCEs)
        scenario = ""
        if "question" in item and "scenario" in item["question"]:
            scenario = item["question"]["scenario"]
        elif "scenario" in item:
            scenario = item["scenario"]
        elif "clinical_scenario" in item:
            scenario = item["clinical_scenario"]

        if scenario and len(scenario) < 50:
            short_scenarios += 1

        # Check explanations
        explanation = ""
        if "explanation" in item:
            explanation = item["explanation"]
        elif "rationale" in item:
            explanation = item["rationale"]

        if explanation and len(explanation) < 100:
            short_explanations += 1

        # Check for patient demographics (age, gender)
        scenario_text = scenario.lower()
        has_age = any(word in scenario_text for word in ["year-old", "yo ", "aged"])
        has_gender = any(word in scenario_text for word in ["man", "woman", "male", "female", "boy", "girl"])

        if scenario and not (has_age and has_gender):
            no_demographics += 1

        # Check for Australian context markers
        content_all = json.dumps(item).lower()
        has_australian = any(marker in content_all for marker in [
            "etg", "therapeutic guidelines", "ranzcp", "amh", "australian",
            "pbs", "medicare", "ahpra", "nsw", "racgp", "000"
        ])

        if not has_australian:
            no_australian += 1

    # Output results
    if short_scenarios > 0:
        print(f"  ⚠️  {short_scenarios} scenarios < 50 characters", file=sys.stderr)
    if short_explanations > 0:
        print(f"  ⚠️  {short_explanations} explanations < 100 characters", file=sys.stderr)
    if no_demographics > 0:
        print(f"  ⚠️  {no_demographics} scenarios missing patient demographics (age/gender)", file=sys.stderr)
    if no_australian > 0:
        print(f"  ⚠️  {no_australian} items missing Australian context markers", file=sys.stderr)

    # Exit with counts
    sys.exit(short_scenarios + short_explanations)

except Exception as e:
    print(f"  ❌ ERROR parsing JSON: {e}", file=sys.stderr)
    sys.exit(1)
EOF

CONTENT_ISSUES=$?

if [ $CONTENT_ISSUES -gt 0 ]; then
    echo -e "${YELLOW}  Found $CONTENT_ISSUES content substance issues (warnings)${NC}"
else
    echo -e "${GREEN}  ✅ Content substance checks passed${NC}"
fi

echo ""

# Final verdict
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $PLACEHOLDER_COUNT -gt 0 ]; then
    echo -e "${RED}❌ VALIDATION FAILED: $PLACEHOLDER_COUNT placeholder patterns detected${NC}"
    echo ""
    echo "CRITICAL ERRORS:"
    echo "  - Placeholder content found (template-only generation)"
    echo "  - Content MUST be regenerated with LLM"
    echo ""
    echo "Actions Required:"
    echo "  1. Regenerate content using LLM (not templates)"
    echo "  2. Ensure RAG citations are extracted: citation['content']"
    echo "  3. Use OllamaClient to generate clinical content"
    echo "  4. Re-run validation: $0 $FILE"
    echo ""
    echo "Reference: constraints/12-content-generation-requirements.md"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 2
elif [ $CONTENT_ISSUES -gt 5 ]; then
    echo -e "${YELLOW}⚠️  VALIDATION WARNING: $CONTENT_ISSUES content quality issues${NC}"
    echo ""
    echo "WARNINGS (not blocking, but should be addressed):"
    echo "  - Short scenarios (<50 chars) or explanations (<100 chars)"
    echo "  - Missing patient demographics (age, gender)"
    echo "  - Missing Australian context markers (eTG, RANZCP, PBS)"
    echo ""
    echo "Consider improving content quality before committing."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo -e "${GREEN}✅ VALIDATION PASSED: Content substance verified${NC}"
    echo ""
    echo "Content Quality Summary:"
    echo "  ✅ No placeholder patterns detected"
    echo "  ✅ Content substance meets minimum requirements"
    echo "  ✅ Ready for QA-003 validation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
fi
