#!/bin/bash
# Complete execution script for respiratory OSCE regeneration

set -e  # Exit on error

echo "========================================"
echo "RESPIRATORY OSCE REGENERATION - 50 OSCEs"
echo "========================================"
echo ""
echo "Started: $(date)"
echo ""

# Navigate to project root
cd /home/dev/Development/irStudy

# Check environment
echo "Step 1: Environment validation..."
echo ""

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set"
    echo "Please set: export ANTHROPIC_API_KEY=your_key_here"
    exit 1
fi
echo "✅ ANTHROPIC_API_KEY configured"

# Check Python
python3 --version
echo "✅ Python available"
echo ""

# Check source file
echo "Step 2: Source file validation..."
echo ""

if [ ! -f "data/osces/respiratory_50_osces.json" ]; then
    echo "ERROR: Source file not found: data/osces/respiratory_50_osces.json"
    exit 1
fi
echo "✅ Source file exists"

# Count OSCEs in source
OSCE_COUNT=$(jq '.osces | length' data/osces/respiratory_50_osces.json)
echo "   OSCEs in source: $OSCE_COUNT"
echo ""

# Baseline placeholder detection
echo "Step 3: Baseline placeholder detection (BEFORE regeneration)..."
echo ""

if [ -f "scripts/detect_placeholder_content.py" ]; then
    python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces.json || true
else
    echo "⚠️  Placeholder detection script not found, skipping baseline"
fi
echo ""

# Execute regeneration
echo "Step 4: Executing regeneration..."
echo ""
echo "CRITICAL CONSTRAINTS:"
echo "  ✓ Spirometry: Specific FEV1/FVC values (not generic)"
echo "  ✓ Oxygen targets: 88-92% COPD, 94-98% non-COPD"
echo "  ✓ Inhaler devices: Specific devices + technique"
echo "  ✓ Medications: Doses + PBS codes"
echo "  ✓ Severity: Mild/moderate/severe/life-threatening"
echo "  ✓ Australian guidelines: Asthma Council, COPD-X, TSANZ"
echo "  ✓ Zero placeholders: No generic phrases"
echo ""
echo "Estimated time: 100-150 minutes (50 OSCEs × 2-3 min each)"
echo "Starting at: $(date '+%H:%M:%S')"
echo ""

# Make script executable
chmod +x scripts/regenerate_respiratory_osces_complete.py

# Run regeneration
python3 scripts/regenerate_respiratory_osces_complete.py \
  data/osces/respiratory_50_osces.json \
  data/osces/respiratory_50_osces_regenerated.json

echo ""
echo "Completed at: $(date '+%H:%M:%S')"
echo ""

# Post-regeneration validation
echo "Step 5: Post-regeneration validation..."
echo ""

# Check output file was created
if [ ! -f "data/osces/respiratory_50_osces_regenerated.json" ]; then
    echo "ERROR: Output file not created"
    exit 1
fi
echo "✅ Output file created"

# Count OSCEs in output
REGEN_COUNT=$(jq '.osces | length' data/osces/respiratory_50_osces_regenerated.json)
echo "   OSCEs regenerated: $REGEN_COUNT"

if [ "$REGEN_COUNT" -ne 50 ]; then
    echo "⚠️  WARNING: Expected 50 OSCEs, found $REGEN_COUNT"
fi
echo ""

# Placeholder detection on regenerated file
echo "Step 6: Placeholder detection (AFTER regeneration)..."
echo ""

if [ -f "scripts/detect_placeholder_content.py" ]; then
    python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces_regenerated.json || true
    echo ""
    echo "EXPECTED: 0% placeholder rate (was 100% before)"
else
    echo "⚠️  Placeholder detection script not found"
fi
echo ""

# Sample validation
echo "Step 7: Sample validation checklist..."
echo ""
echo "MANUAL SPOT CHECK REQUIRED (3 random OSCEs):"
echo ""
echo "For each sampled OSCE, verify:"
echo "  [ ] Spirometry: Specific FEV1/FVC values with interpretation"
echo "      Example: 'FEV1 1.2L (40% predicted), FVC 2.8L (85% predicted)'"
echo ""
echo "  [ ] Oxygen targets: Correct for condition"
echo "      COPD: 88-92% (Venturi mask 28%)"
echo "      Non-COPD: 94-98% (Hudson mask 8-10L/min)"
echo ""
echo "  [ ] Inhaler devices: Specific devices + technique"
echo "      Example: 'Salbutamol 200mcg via MDI + spacer (shake, breathe out, press, hold 10 sec)'"
echo ""
echo "  [ ] Medications: Doses + PBS codes"
echo "      Example: 'Prednisolone 50mg PO stat, PBS 1234K'"
echo ""
echo "  [ ] Severity classification: Explicit classification"
echo "      Example: 'ACUTE SEVERE ASTHMA (per National Asthma Council): Unable to speak...'"
echo ""
echo "  [ ] No generic phrases"
echo "      ❌ 'A patient presents with shortness of breath'"
echo "      ✅ '28-year-old office worker with known asthma...'"
echo ""
echo "  [ ] Complete marking criteria (10-15 items)"
echo ""
echo "  [ ] Australian guidelines referenced"
echo "      National Asthma Council, COPD-X Guidelines, TSANZ, eTG"
echo ""

# Sample 3 random OSCEs for manual review
echo "Sampling 3 random OSCEs for manual review..."
echo ""

jq '.osces | .[5,15,25] | {osce_id, topic, candidate_instructions: .candidate_instructions[:150]}' \
  data/osces/respiratory_50_osces_regenerated.json

echo ""

# Quality gate summary
echo "Step 8: Quality gates summary..."
echo ""
echo "QUALITY GATES (ALL MUST PASS):"
echo ""

# Gate 1: File created
if [ -f "data/osces/respiratory_50_osces_regenerated.json" ]; then
    echo "✅ Gate 1: Output file created"
else
    echo "❌ Gate 1: Output file NOT created"
fi

# Gate 2: Correct count
if [ "$REGEN_COUNT" -eq 50 ]; then
    echo "✅ Gate 2: All 50 OSCEs regenerated"
else
    echo "❌ Gate 2: Only $REGEN_COUNT OSCEs regenerated (expected 50)"
fi

# Gate 3-8: Manual validation required
echo "⚠️  Gate 3: Spirometry values specific (MANUAL CHECK REQUIRED)"
echo "⚠️  Gate 4: Oxygen targets correct (MANUAL CHECK REQUIRED)"
echo "⚠️  Gate 5: Inhaler devices specified (MANUAL CHECK REQUIRED)"
echo "⚠️  Gate 6: Medications have doses + PBS (MANUAL CHECK REQUIRED)"
echo "⚠️  Gate 7: Australian guidelines referenced (MANUAL CHECK REQUIRED)"
echo "⚠️  Gate 8: 0% placeholder rate (CHECK detect_placeholder_content.py OUTPUT)"

echo ""
echo "========================================"
echo "REGENERATION COMPLETE"
echo "========================================"
echo ""
echo "Finished: $(date)"
echo ""
echo "Output file: data/osces/respiratory_50_osces_regenerated.json"
echo ""
echo "NEXT STEPS:"
echo "1. Review placeholder detection results above (should be 0%)"
echo "2. Manually spot check 3 sampled OSCEs (shown above)"
echo "3. Verify all quality gates PASS"
echo "4. If all checks pass, backup and replace original file:"
echo ""
echo "   cp data/osces/respiratory_50_osces.json data/osces/respiratory_50_osces_backup_$(date +%Y%m%d).json"
echo "   cp data/osces/respiratory_50_osces_regenerated.json data/osces/respiratory_50_osces.json"
echo ""
echo "5. Commit changes to git"
echo ""
