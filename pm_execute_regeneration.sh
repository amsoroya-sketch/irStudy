#!/bin/bash
# PM Coordination Script for Cardiology OSCE Regeneration
set -e

cd /home/dev/Development/irStudy

echo "============================================"
echo "PM: CARDIOLOGY OSCE REGENERATION COORDINATION"
echo "============================================"
echo ""

# Step 1: Check if scripts exist
echo "Step 1: Checking existing scripts..."
if [ -f "scripts/regenerate_cardiology_osces.py" ]; then
    echo "✅ Regeneration script exists"
    echo "Showing first 50 lines:"
    head -50 scripts/regenerate_cardiology_osces.py
    USE_EXISTING=true
else
    echo "❌ Regeneration script does NOT exist"
    echo "Will create new script"
    USE_EXISTING=false
fi
echo ""

# Step 2: Check source data
echo "Step 2: Checking source data files..."
if [ -f "data/osces/cardiology_50_osces.json" ]; then
    OSCE_COUNT=$(python3 -c "import json; print(len(json.load(open('data/osces/cardiology_50_osces.json'))))")
    echo "✅ Source file exists with $OSCE_COUNT OSCEs"
else
    echo "❌ Source file NOT found: data/osces/cardiology_50_osces.json"
    exit 1
fi

if [ -f "data/osces/psychiatry_week1_osces.json" ]; then
    echo "✅ Gold standard template exists"
else
    echo "❌ Gold standard template NOT found: data/osces/psychiatry_week1_osces.json"
    exit 1
fi
echo ""

# Step 3: Check placeholder detection script
echo "Step 3: Checking placeholder detection script..."
if [ -f "scripts/detect_placeholder_content.py" ]; then
    echo "✅ Placeholder detection script exists"
else
    echo "❌ Placeholder detection script NOT found"
    echo "This is needed for validation"
fi
echo ""

# Step 4: Check API key
echo "Step 4: Verifying Claude API key..."
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY is set"
elif [ -n "$CLAUDE_API_KEY" ]; then
    echo "⚠️  CLAUDE_API_KEY found, setting ANTHROPIC_API_KEY"
    export ANTHROPIC_API_KEY="$CLAUDE_API_KEY"
else
    echo "❌ No API key found. Please set ANTHROPIC_API_KEY or CLAUDE_API_KEY"
    exit 1
fi
echo ""

# Step 5: Pre-flight validation
echo "Step 5: Running pre-flight checks..."
if [ -f "scripts/pre_flight_validation.sh" ]; then
    echo "Running pre-flight validation..."
    bash scripts/pre_flight_validation.sh || echo "⚠️  Pre-flight checks had issues (continuing anyway)"
else
    echo "⚠️  Pre-flight validation script not found (skipping)"
fi
echo ""

echo "============================================"
echo "PRE-FLIGHT COMPLETE - READY TO REGENERATE"
echo "============================================"
echo ""
echo "Summary:"
echo "  - Source OSCEs: $OSCE_COUNT"
echo "  - Regeneration script: $([ "$USE_EXISTING" = "true" ] && echo "EXISTS" || echo "NEEDS CREATION")"
echo "  - API key: CONFIGURED"
echo ""
echo "Next steps:"
echo "  1. Create/verify regeneration script"
echo "  2. Execute regeneration (100-150 minutes)"
echo "  3. Validate output (placeholder detection + spot checks)"
echo ""
