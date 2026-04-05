#!/bin/bash
# Master Execution Script for Cardiology OSCE Regeneration
# This script coordinates the entire regeneration workflow

set -e  # Exit on error

cd /home/dev/Development/irStudy

echo "════════════════════════════════════════════════════════════════"
echo "CARDIOLOGY OSCE REGENERATION - MASTER EXECUTION SCRIPT"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This script will:"
echo "  1. Validate prerequisites (API key, input files)"
echo "  2. Check current placeholder rate"
echo "  3. Regenerate 50 cardiology OSCEs (100-150 minutes)"
echo "  4. Validate results (placeholder detection + spot checks)"
echo "  5. Generate quality report"
echo ""
echo "Start time: $(date)"
echo ""

# ============================================================================
# STEP 1: PRE-FLIGHT VALIDATION
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "STEP 1: PRE-FLIGHT VALIDATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check API key
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY is set"
elif [ -n "$CLAUDE_API_KEY" ]; then
    echo "⚠️  CLAUDE_API_KEY found, setting ANTHROPIC_API_KEY"
    export ANTHROPIC_API_KEY="$CLAUDE_API_KEY"
else
    echo "❌ ERROR: No API key found"
    echo ""
    echo "Please set API key with:"
    echo "    export ANTHROPIC_API_KEY='your-key-here'"
    echo "Or:"
    echo "    export CLAUDE_API_KEY='your-key-here'"
    echo ""
    exit 1
fi

# Check Python dependencies
echo ""
echo "Checking Python dependencies..."
python3 -c "import anthropic" 2>/dev/null && echo "✅ anthropic library installed" || {
    echo "❌ anthropic library NOT installed"
    echo "Install with: pip install anthropic"
    exit 1
}

# Check input file
echo ""
echo "Checking input file..."
if [ -f "data/osces/cardiology_50_osces.json" ]; then
    OSCE_COUNT=$(python3 -c "import json; print(len(json.load(open('data/osces/cardiology_50_osces.json'))))" 2>/dev/null || echo "0")
    if [ "$OSCE_COUNT" -eq "50" ]; then
        echo "✅ Input file exists with $OSCE_COUNT OSCEs"
    else
        echo "⚠️  Input file exists but has $OSCE_COUNT OSCEs (expected 50)"
    fi
else
    echo "❌ ERROR: Input file not found: data/osces/cardiology_50_osces.json"
    exit 1
fi

# Check gold standard template
echo ""
echo "Checking gold standard template..."
if [ -f "data/osces/psychiatry_week1_osces.json" ]; then
    echo "✅ Gold standard template exists"
else
    echo "⚠️  WARNING: Gold standard template not found"
    echo "   Will use default structure"
fi

# Check regeneration script
echo ""
echo "Checking regeneration script..."
if [ -f "scripts/regenerate_cardiology_osces_complete.py" ]; then
    echo "✅ Regeneration script exists"
    chmod +x scripts/regenerate_cardiology_osces_complete.py
else
    echo "❌ ERROR: Regeneration script not found"
    exit 1
fi

# Check placeholder detection script
echo ""
echo "Checking placeholder detection script..."
if [ -f "scripts/detect_placeholder_content.py" ]; then
    echo "✅ Placeholder detection script exists"
else
    echo "⚠️  WARNING: Placeholder detection script not found"
    echo "   Will skip placeholder detection validation"
fi

echo ""
echo "✅ PRE-FLIGHT VALIDATION COMPLETE"
echo ""

# ============================================================================
# STEP 2: BASELINE PLACEHOLDER DETECTION
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "STEP 2: BASELINE PLACEHOLDER DETECTION"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "scripts/detect_placeholder_content.py" ]; then
    echo "Detecting placeholders in original file..."
    python3 scripts/detect_placeholder_content.py data/osces/cardiology_50_osces.json > placeholder_before.txt 2>&1 || true
    cat placeholder_before.txt
    echo ""
else
    echo "⚠️  Skipping (detection script not found)"
    echo ""
fi

# ============================================================================
# STEP 3: REGENERATION (THIS WILL TAKE 100-150 MINUTES)
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "STEP 3: OSCE REGENERATION (100-150 MINUTES)"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⏱️  Estimated time: 100-150 minutes (50 OSCEs × 2-3 min each)"
echo ""
echo "Regeneration will:"
echo "  - Generate complete clinical content for each OSCE"
echo "  - Include specific ECG findings (NOT 'ECG changes for...')"
echo "  - Include medications with doses + PBS codes"
echo "  - Include Australian guidelines (Heart Foundation, CSANZ, eTG)"
echo "  - Eliminate ALL placeholder phrases"
echo ""

read -p "Press ENTER to start regeneration (or Ctrl+C to cancel)..."
echo ""

REGENERATION_START=$(date +%s)

python3 scripts/regenerate_cardiology_osces_complete.py \
    data/osces/cardiology_50_osces.json \
    data/osces/cardiology_50_osces_regenerated.json

REGENERATION_END=$(date +%s)
REGENERATION_TIME=$((REGENERATION_END - REGENERATION_START))
REGENERATION_MINUTES=$((REGENERATION_TIME / 60))

echo ""
echo "✅ REGENERATION COMPLETE"
echo "   Time taken: $REGENERATION_MINUTES minutes ($REGENERATION_TIME seconds)"
echo ""

# ============================================================================
# STEP 4: POST-REGENERATION VALIDATION
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "STEP 4: POST-REGENERATION VALIDATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Count OSCEs
echo "Counting regenerated OSCEs..."
REGENERATED_COUNT=$(python3 -c "import json; print(len(json.load(open('data/osces/cardiology_50_osces_regenerated.json'))))" 2>/dev/null || echo "0")
echo "Total OSCEs: $REGENERATED_COUNT/50"
echo ""

# Placeholder detection
if [ -f "scripts/detect_placeholder_content.py" ]; then
    echo "Detecting placeholders in regenerated file..."
    python3 scripts/detect_placeholder_content.py data/osces/cardiology_50_osces_regenerated.json > placeholder_after.txt 2>&1 || true
    cat placeholder_after.txt
    echo ""
else
    echo "⚠️  Skipping placeholder detection (script not found)"
    echo ""
fi

# ============================================================================
# STEP 5: SPOT CHECK VALIDATION
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "STEP 5: SPOT CHECK VALIDATION (3 RANDOM OSCEs)"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 << 'PYTHON_SPOT_CHECK'
import json
import random

with open('data/osces/cardiology_50_osces_regenerated.json') as f:
    osces = json.load(f)

# Select 3 random OSCEs
random.seed(42)
sample = random.sample(osces, min(3, len(osces)))

for i, osce in enumerate(sample, 1):
    print(f"\n{'='*70}")
    print(f"SPOT CHECK {i}: {osce.get('title', 'Unknown')}")
    print(f"{'='*70}")
    print(f"Topic: {osce.get('topic', 'Unknown')}")
    print(f"Difficulty: {osce.get('difficulty', 'Unknown')}")
    print()

    # Check candidate instructions
    cand_instr = osce.get('candidate_instructions', '')
    print(f"Candidate Instructions:")
    print(f"  Length: {len(cand_instr)} chars")
    if len(cand_instr) < 200:
        print(f"  ❌ TOO SHORT (should be >200 chars)")
    else:
        print(f"  ✅ Adequate length")
        print(f"  Preview: {cand_instr[:150]}...")

    # Check for placeholder phrases
    placeholders = [
        'A patient presents with',
        'According to Australian guidelines',
        'ECG findings for',
        'Management as per protocol',
        'as per guidelines'
    ]

    full_text = json.dumps(osce).lower()
    found = [p for p in placeholders if p.lower() in full_text]
    print()
    print(f"Placeholder Check:")
    if found:
        print(f"  ❌ PLACEHOLDERS FOUND: {found}")
    else:
        print(f"  ✅ No placeholder phrases detected")

    # Check sample answer structure
    sample_ans = osce.get('sample_answer', {})
    print()
    print(f"Sample Answer Structure:")

    if isinstance(sample_ans, dict):
        # Check for ECG findings
        ecg = sample_ans.get('ecg_findings', '') or sample_ans.get('assessment', '') or ''
        if ecg:
            if 'ECG findings for' in ecg or 'ECG changes consistent with' in ecg:
                print(f"  ❌ Generic ECG description")
            elif len(ecg) > 100 and ('mm' in ecg or 'bpm' in ecg or 'leads' in ecg.lower()):
                print(f"  ✅ Specific ECG findings present")
                print(f"     Preview: {ecg[:120]}...")
            else:
                print(f"  ⚠️  ECG findings may be insufficient")
        else:
            print(f"  ⚠️  No ECG findings section (may not be applicable)")

        # Check for medications with doses
        mgmt_text = str(sample_ans.get('immediate_management', '')) + \
                    str(sample_ans.get('ongoing_management', ''))

        print()
        print(f"Medication Management:")
        if 'mg' in mgmt_text and 'PBS' in mgmt_text:
            print(f"  ✅ Medications with doses AND PBS codes")
            # Extract example
            lines = mgmt_text.split('\n') if '\n' in mgmt_text else [mgmt_text]
            med_examples = [l for l in lines if 'mg' in l and 'PBS' in l][:2]
            for ex in med_examples:
                print(f"     Example: {ex[:100]}...")
        elif 'mg' in mgmt_text:
            print(f"  ⚠️  Medications with doses but MISSING PBS codes")
        else:
            print(f"  ❌ No specific medication doses found")

        # Check for specific timelines (STEMI protocol)
        if 'door-to-balloon' in mgmt_text.lower() or '90 min' in mgmt_text.lower():
            print()
            print(f"STEMI Protocol:")
            print(f"  ✅ Door-to-balloon time specified")
        elif 'stemi' in full_text.lower() or 'myocardial infarction' in full_text.lower():
            print()
            print(f"STEMI Protocol:")
            print(f"  ⚠️  STEMI case but no door-to-balloon time")

    # Check learning points
    learning = osce.get('learning_points', [])
    print()
    print(f"Learning Points: {len(learning)} items")
    if len(learning) >= 6:
        print(f"  ✅ Adequate number (≥6)")
        print(f"     Example: {learning[0][:100]}...")
    elif len(learning) >= 3:
        print(f"  ⚠️  Could use more (3-5 present, 6-8 recommended)")
    else:
        print(f"  ❌ Insufficient (<3)")

    # Check marking criteria
    marking = osce.get('marking_criteria', [])
    print()
    print(f"Marking Criteria: {len(marking)} items")
    if len(marking) >= 10:
        print(f"  ✅ Comprehensive (≥10)")
    elif len(marking) >= 6:
        print(f"  ⚠️  Adequate (6-9 items)")
    else:
        print(f"  ❌ Insufficient (<6)")

print()
print('='*70)
print("SPOT CHECK COMPLETE")
print('='*70)
PYTHON_SPOT_CHECK

echo ""

# ============================================================================
# STEP 6: QUALITY GATE SUMMARY
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "STEP 6: QUALITY GATE SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Generate quality gate checklist
python3 << 'PYTHON_QUALITY_GATES'
import json

with open('data/osces/cardiology_50_osces_regenerated.json') as f:
    osces = json.load(f)

print("Quality Gate Checklist:")
print()

# Gate 1: Count
total = len(osces)
print(f"Gate 1: OSCE Count")
if total == 50:
    print(f"  ✅ PASS: {total}/50 OSCEs generated")
else:
    print(f"  ❌ FAIL: {total}/50 OSCEs generated")
print()

# Gate 2: Candidate instructions length
short_instructions = sum(1 for o in osces if len(o.get('candidate_instructions', '')) < 200)
print(f"Gate 2: Candidate Instructions Length")
if short_instructions == 0:
    print(f"  ✅ PASS: All OSCEs have adequate instructions (>200 chars)")
else:
    print(f"  ⚠️  WARNING: {short_instructions} OSCEs have short instructions")
print()

# Gate 3: Placeholder phrases
placeholders = [
    'A patient presents with',
    'According to Australian guidelines',
    'ECG findings for',
    'Management as per protocol',
    'as per guidelines'
]

osces_with_placeholders = 0
for osce in osces:
    text = json.dumps(osce).lower()
    if any(p.lower() in text for p in placeholders):
        osces_with_placeholders += 1

print(f"Gate 3: Placeholder Phrases")
if osces_with_placeholders == 0:
    print(f"  ✅ PASS: No placeholder phrases detected")
else:
    print(f"  ❌ FAIL: {osces_with_placeholders} OSCEs contain placeholder phrases")
print()

# Gate 4: Medications with doses
osces_with_doses = 0
for osce in osces:
    sample_ans = osce.get('sample_answer', {})
    mgmt = str(sample_ans.get('immediate_management', '')) + \
           str(sample_ans.get('ongoing_management', ''))
    if 'mg' in mgmt:
        osces_with_doses += 1

print(f"Gate 4: Medications with Doses")
pct_doses = (osces_with_doses / total * 100) if total > 0 else 0
if osces_with_doses >= total * 0.8:  # 80% threshold
    print(f"  ✅ PASS: {osces_with_doses}/{total} OSCEs ({pct_doses:.0f}%) have medication doses")
else:
    print(f"  ⚠️  WARNING: {osces_with_doses}/{total} OSCEs ({pct_doses:.0f}%) have medication doses")
print()

# Gate 5: PBS codes
osces_with_pbs = 0
for osce in osces:
    sample_ans = osce.get('sample_answer', {})
    mgmt = str(sample_ans.get('immediate_management', '')) + \
           str(sample_ans.get('ongoing_management', ''))
    if 'PBS' in mgmt:
        osces_with_pbs += 1

print(f"Gate 5: PBS Codes")
pct_pbs = (osces_with_pbs / total * 100) if total > 0 else 0
if osces_with_pbs >= total * 0.6:  # 60% threshold (not all OSCEs may have medications)
    print(f"  ✅ PASS: {osces_with_pbs}/{total} OSCEs ({pct_pbs:.0f}%) have PBS codes")
else:
    print(f"  ⚠️  WARNING: {osces_with_pbs}/{total} OSCEs ({pct_pbs:.0f}%) have PBS codes")
print()

# Gate 6: Learning points
osces_with_learning = sum(1 for o in osces if len(o.get('learning_points', [])) >= 5)
print(f"Gate 6: Learning Points")
if osces_with_learning >= total * 0.9:
    print(f"  ✅ PASS: {osces_with_learning}/{total} OSCEs have ≥5 learning points")
else:
    print(f"  ⚠️  WARNING: {osces_with_learning}/{total} OSCEs have ≥5 learning points")
print()

# Overall assessment
print("="*70)
print("OVERALL ASSESSMENT:")
print("="*70)

pass_count = 0
fail_count = 0
warning_count = 0

if total == 50:
    pass_count += 1
else:
    fail_count += 1

if short_instructions == 0:
    pass_count += 1
else:
    warning_count += 1

if osces_with_placeholders == 0:
    pass_count += 1
else:
    fail_count += 1

if osces_with_doses >= total * 0.8:
    pass_count += 1
else:
    warning_count += 1

if osces_with_pbs >= total * 0.6:
    pass_count += 1
else:
    warning_count += 1

if osces_with_learning >= total * 0.9:
    pass_count += 1
else:
    warning_count += 1

print(f"PASS: {pass_count}/6 gates")
print(f"WARNING: {warning_count}/6 gates")
print(f"FAIL: {fail_count}/6 gates")
print()

if fail_count == 0 and warning_count <= 2:
    print("✅ DEPLOYMENT READY")
    print("   All critical gates passed, minor warnings acceptable")
elif fail_count == 0:
    print("⚠️  REVIEW RECOMMENDED")
    print("   No critical failures but multiple warnings")
else:
    print("❌ NEEDS REWORK")
    print("   Critical gates failed, regeneration may be needed")

PYTHON_QUALITY_GATES

echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "REGENERATION COMPLETE - FINAL SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Files:"
echo "  Input:  data/osces/cardiology_50_osces.json"
echo "  Output: data/osces/cardiology_50_osces_regenerated.json"
echo ""
echo "Logs:"
echo "  Placeholder before: placeholder_before.txt"
echo "  Placeholder after:  placeholder_after.txt"
echo ""
echo "Total time: $REGENERATION_MINUTES minutes"
echo "End time: $(date)"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "NEXT STEPS"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "1. Review quality gate summary above"
echo ""
echo "2. If DEPLOYMENT READY, replace original file:"
echo "   cp data/osces/cardiology_50_osces_regenerated.json \\"
echo "      data/osces/cardiology_50_osces.json"
echo ""
echo "3. If REVIEW RECOMMENDED, manually check flagged OSCEs:"
echo "   - OSCEs with placeholder phrases"
echo "   - OSCEs with missing PBS codes"
echo "   - OSCEs with short candidate instructions"
echo ""
echo "4. If NEEDS REWORK, consider:"
echo "   - Regenerating specific OSCEs (edit and re-run script)"
echo "   - Adjusting prompts for better clinical detail"
echo "   - Manual clinical review and editing"
echo ""
echo "5. Commit to git:"
echo "   git add data/osces/cardiology_50_osces.json"
echo "   git commit -m 'feat(osces): Regenerate 50 cardiology OSCEs with complete clinical content (ZERO placeholders)'"
echo ""
echo "════════════════════════════════════════════════════════════════"
