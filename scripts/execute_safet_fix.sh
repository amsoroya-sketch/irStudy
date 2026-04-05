#!/bin/bash
# Execute SAFE-T violation fix with full reporting
# CRITICAL: Fixes ZERO-TOLERANCE violation for suicide risk assessment

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCQ_FILE="$PROJECT_ROOT/data/mcqs/week1_all_100_unique_mcqs.json"
BACKUP_DIR="$PROJECT_ROOT/data/mcqs/backups"

echo "================================================================================"
echo "SAFE-T VIOLATION FIX - EXECUTION"
echo "================================================================================"
echo ""
echo "Target File: $MCQ_FILE"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Step 1: Create backup
echo "Step 1: Creating backup..."
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/week1_all_100_unique_mcqs_backup_$(date +%Y%m%d_%H%M%S).json"
cp "$MCQ_FILE" "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"
echo ""

# Step 2: Inspect current state
echo "Step 2: Inspecting current state..."
python3 "$SCRIPT_DIR/inspect_mcq_structure.py"
echo ""

# Step 3: Run fix script
echo "Step 3: Running SAFE-T fix script..."
python3 "$SCRIPT_DIR/fix_safet_violations.py"
echo ""

# Step 4: Validate JSON
echo "Step 4: Validating JSON integrity..."
if python3 -m json.tool "$MCQ_FILE" > /dev/null 2>&1; then
    echo "✅ JSON validation PASSED"
else
    echo "❌ JSON validation FAILED"
    echo "   Restoring from backup..."
    cp "$BACKUP_FILE" "$MCQ_FILE"
    exit 1
fi
echo ""

# Step 5: Content validation
echo "Step 5: Content validation..."

# Count SAFE-T occurrences
SAFET_COUNT=$(grep -c "SAFE-T suicide risk assessment" "$MCQ_FILE" || true)
echo "  SAFE-T key points found: $SAFET_COUNT"

# Count crisis contacts
CRISIS_COUNT=$(grep -c "Lifeline 13 11 14" "$MCQ_FILE" || true)
echo "  Crisis contact key points found: $CRISIS_COUNT"

# Count Australian references
REF_COUNT=$(grep -c "RANZCP\|Black Dog Institute\|Therapeutic Guidelines" "$MCQ_FILE" || true)
echo "  Australian references found: $REF_COUNT"

# File size comparison
ORIGINAL_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
NEW_SIZE=$(stat -f%z "$MCQ_FILE" 2>/dev/null || stat -c%s "$MCQ_FILE" 2>/dev/null)
SIZE_INCREASE=$((NEW_SIZE - ORIGINAL_SIZE))

echo ""
echo "  File size: $ORIGINAL_SIZE → $NEW_SIZE bytes (+$SIZE_INCREASE bytes)"

if [ $SIZE_INCREASE -gt 0 ]; then
    echo "  ✅ Content added successfully"
else
    echo "  ⚠️  Warning: File size did not increase"
fi
echo ""

# Step 6: Generate summary
echo "================================================================================"
echo "FIX EXECUTION COMPLETE"
echo "================================================================================"
echo ""
echo "Summary:"
echo "  - Backup: $BACKUP_FILE"
echo "  - SAFE-T content added: $SAFET_COUNT instances"
echo "  - Crisis contacts added: $CRISIS_COUNT instances"
echo "  - Australian references: $REF_COUNT instances"
echo "  - Size increase: +$SIZE_INCREASE bytes"
echo ""
echo "Next Steps:"
echo "  1. Review detailed report: $PROJECT_ROOT/SAFET_VIOLATION_FIX_REPORT.md"
echo "  2. Run re-evaluation:"
echo "     cd evaluation-system"
echo "     python3 evaluate_content.py \\"
echo "       --file ../data/mcqs/week1_all_100_unique_mcqs.json \\"
echo "       --content-type mcq \\"
echo "       --output-dir reports/safet_fixed_\$(date +%Y%m%d_%H%M%S)"
echo ""
echo "  3. Verify Mental Health Crisis Expert score ≥9.0/10 on suicide_risk_safe_t"
echo "  4. Verify Gate 13 Educational Alignment: PASS"
echo ""
echo "================================================================================"
