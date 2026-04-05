#!/bin/bash
set -e

echo "============================================"
echo "CARDIOLOGY OSCE REGENERATION - STARTING"
echo "============================================"
echo ""

# Navigate to project root
cd /home/dev/Development/irStudy

# Check current placeholder rate
echo "Step 1: Checking current placeholder rate..."
python3 scripts/detect_placeholder_content.py data/osces/cardiology_50_osces.json | tee placeholder_before.txt
echo ""

# Execute regeneration
echo "Step 2: Regenerating 50 cardiology OSCEs with full clinical content..."
echo "This will take approximately 100-150 minutes (50 OSCEs × 2-3 min each)"
echo "Start time: $(date)"
echo ""

python3 scripts/regenerate_cardiology_osces.py \
  data/osces/cardiology_50_osces.json \
  data/osces/cardiology_50_osces_regenerated.json

echo ""
echo "End time: $(date)"
echo ""

# Validate results
echo "Step 3: Validating regenerated OSCEs..."
python3 scripts/detect_placeholder_content.py data/osces/cardiology_50_osces_regenerated.json | tee placeholder_after.txt
echo ""

# Count OSCEs
echo "Step 4: Counting generated OSCEs..."
OSCE_COUNT=$(python3 -c "import json; data = json.load(open('data/osces/cardiology_50_osces_regenerated.json')); print(len(data))")
echo "Total OSCEs generated: $OSCE_COUNT/50"
echo ""

# Spot check 3 random OSCEs
echo "Step 5: Spot checking 3 random OSCEs for quality..."
python3 -c "
import json
import random

with open('data/osces/cardiology_50_osces_regenerated.json') as f:
    osces = json.load(f)

# Select 3 random OSCEs
random.seed(42)
sample = random.sample(osces, min(3, len(osces)))

for i, osce in enumerate(sample, 1):
    print(f'\n=== SPOT CHECK {i}: {osce.get(\"title\", \"Unknown\")} ===')
    print(f'Topic: {osce.get(\"topic\", \"Unknown\")}')

    # Check candidate instructions length
    cand_instr = osce.get('candidate_instructions', '')
    print(f'Candidate instructions length: {len(cand_instr)} chars')
    if len(cand_instr) < 200:
        print('  ⚠️  WARNING: Instructions too short')
    else:
        print('  ✅ Instructions adequate length')

    # Check for placeholder phrases
    placeholders = [
        'A patient presents with',
        'According to Australian guidelines',
        'ECG findings for',
        'Management as per protocol',
        'as per guidelines'
    ]
    found_placeholders = [p for p in placeholders if p.lower() in cand_instr.lower()]
    if found_placeholders:
        print(f'  ❌ Placeholder phrases found: {found_placeholders}')
    else:
        print('  ✅ No placeholder phrases')

    # Check sample answer
    sample_ans = osce.get('sample_answer', {})
    if isinstance(sample_ans, dict):
        # Check for specific ECG findings
        ecg = sample_ans.get('ecg_findings', '') or sample_ans.get('assessment', '')
        if 'ECG findings for' in ecg or 'ECG changes consistent with' in ecg:
            print('  ❌ Generic ECG description found')
        elif len(ecg) > 100:
            print('  ✅ Specific ECG findings present')
        else:
            print('  ⚠️  ECG findings may be insufficient')

        # Check for medications with doses
        mgmt = str(sample_ans.get('immediate_management', '')) + str(sample_ans.get('ongoing_management', ''))
        if 'mg' in mgmt and ('PBS' in mgmt or 'MBS' in mgmt):
            print('  ✅ Medications with doses and PBS codes')
        elif 'mg' in mgmt:
            print('  ⚠️  Medications with doses but missing PBS codes')
        else:
            print('  ❌ No specific medication doses found')

    # Check learning points
    learning = osce.get('learning_points', [])
    if len(learning) >= 5:
        print(f'  ✅ Learning points: {len(learning)} items')
    else:
        print(f'  ⚠️  Learning points: {len(learning)} items (should be ≥5)')

    print()
"
echo ""

echo "============================================"
echo "REGENERATION COMPLETE"
echo "============================================"
echo ""
echo "Summary:"
echo "  - OSCEs generated: $OSCE_COUNT/50"
echo "  - Output file: data/osces/cardiology_50_osces_regenerated.json"
echo ""
echo "Next steps:"
echo "  1. Review spot check results above"
echo "  2. Manually review 2-3 OSCEs for clinical accuracy"
echo "  3. Compare placeholder rates (before vs after)"
echo "  4. If all quality gates pass, replace original file"
echo ""
