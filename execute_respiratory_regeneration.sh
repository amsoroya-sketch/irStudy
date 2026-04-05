#!/bin/bash
# Execute respiratory OSCE regeneration with validation

set -e  # Exit on error

echo "========================================"
echo "RESPIRATORY OSCE REGENERATION - 50 OSCEs"
echo "========================================"
echo ""

# Navigate to project root
cd /home/dev/Development/irStudy

# Pre-flight checks
echo "Step 1: Pre-flight validation..."
echo ""

# Check if source file exists
if [ ! -f "data/osces/respiratory_50_osces.json" ]; then
    echo "ERROR: Source file not found: data/osces/respiratory_50_osces.json"
    exit 1
fi

# Check if regeneration script exists
if [ ! -f "scripts/regenerate_respiratory_osces.py" ]; then
    echo "ERROR: Regeneration script not found: scripts/regenerate_respiratory_osces.py"
    exit 1
fi

# Check placeholder detection script
if [ ! -f "scripts/detect_placeholder_content.py" ]; then
    echo "ERROR: Placeholder detection script not found"
    exit 1
fi

echo "✅ All required files present"
echo ""

# Baseline placeholder detection
echo "Step 2: Baseline placeholder detection (before regeneration)..."
echo ""
python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces.json
echo ""

# Execute regeneration
echo "Step 3: Executing regeneration (50 OSCEs)..."
echo "Estimated time: 100-150 minutes"
echo ""
python3 scripts/regenerate_respiratory_osces.py \
  data/osces/respiratory_50_osces.json \
  data/osces/respiratory_50_osces_regenerated.json

echo ""
echo "Step 4: Post-regeneration placeholder detection..."
echo ""
python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces_regenerated.json

echo ""
echo "Step 5: Sample validation (3 random OSCEs)..."
echo ""
# This would be manual spot checking in practice
echo "Manual spot check required for:"
echo "1. Spirometry: Specific FEV1/FVC values with interpretation"
echo "2. Oxygen targets: Correct for condition (88-92% COPD vs 94-98% non-COPD)"
echo "3. Inhaler devices: Specific devices + technique instructions"
echo "4. Medications: Doses + PBS codes"
echo "5. Severity classification: Mild/moderate/severe/life-threatening"
echo "6. No generic phrases"
echo "7. Complete marking criteria (10-15 items)"
echo "8. Australian guidelines referenced"

echo ""
echo "========================================"
echo "REGENERATION COMPLETE"
echo "========================================"
echo ""
echo "Output file: data/osces/respiratory_50_osces_regenerated.json"
echo ""
echo "Next steps:"
echo "1. Review placeholder detection results (should be 0%)"
echo "2. Manually spot check 3 random OSCEs"
echo "3. Validate all quality gates passed"
echo "4. Replace original file if all checks pass"
