#!/bin/bash
set -e

echo "=========================================="
echo "RESPIRATORY OSCE REGENERATION - EXECUTION"
echo "=========================================="
echo ""

cd /home/dev/Development/irStudy

echo "[1/10] Checking prerequisites..."
echo "- Checking input file exists..."
if [ ! -f "data/osces/respiratory_50_osces.json" ]; then
    echo "ERROR: Input file not found!"
    exit 1
fi
echo "  ✓ Input file exists"

echo "- Checking script exists..."
if [ ! -f "scripts/regenerate_respiratory_osces.py" ]; then
    echo "ERROR: Regeneration script not found!"
    exit 1
fi
echo "  ✓ Script exists"

echo ""
echo "[2/10] Pre-regeneration baseline check..."
echo "Current placeholder rate:"
python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces.json || true

echo ""
echo "[3/10] Starting regeneration (50 OSCEs)..."
echo "Expected time: 100-150 minutes"
echo "Start time: $(date)"
echo ""

python3 scripts/regenerate_respiratory_osces.py \
  data/osces/respiratory_50_osces.json \
  data/osces/respiratory_50_osces_regenerated.json

echo ""
echo "End time: $(date)"
echo ""

echo "[4/10] Validating file creation..."
if [ ! -f "data/osces/respiratory_50_osces_regenerated.json" ]; then
    echo "ERROR: Output file not created!"
    exit 1
fi

echo "File size:"
ls -lh data/osces/respiratory_50_osces_regenerated.json
echo ""

echo "Line count:"
wc -l data/osces/respiratory_50_osces_regenerated.json
echo ""

echo "[5/10] Validating JSON structure..."
python3 -m json.tool data/osces/respiratory_50_osces_regenerated.json > /dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ JSON is valid"
else
    echo "  ✗ JSON validation failed!"
    exit 1
fi
echo ""

echo "[6/10] Counting OSCEs generated..."
python3 -c "
import json
with open('data/osces/respiratory_50_osces_regenerated.json') as f:
    data = json.load(f)
osce_count = len(data.get('osces', []))
print(f'OSCEs generated: {osce_count}')
if osce_count != 50:
    print(f'ERROR: Expected 50 OSCEs, got {osce_count}')
    exit(1)
"
echo ""

echo "[7/10] CRITICAL: Checking placeholder rate..."
python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces_regenerated.json
echo ""

echo "[8/10] Quality Gate 1: Spirometry values..."
spirometry_count=$(grep -o "FEV1.*L.*predicted" data/osces/respiratory_50_osces_regenerated.json | wc -l)
echo "Spirometry mentions found: $spirometry_count"
if [ $spirometry_count -ge 40 ]; then
    echo "  ✓ PASS (≥40 required)"
else
    echo "  ✗ FAIL (≥40 required, got $spirometry_count)"
fi
echo ""

echo "[8/10] Quality Gate 2: Oxygen targets..."
oxygen_count=$(grep -E "88-92%|94-98%" data/osces/respiratory_50_osces_regenerated.json | wc -l)
echo "Oxygen target specifications found: $oxygen_count"
if [ $oxygen_count -ge 30 ]; then
    echo "  ✓ PASS (≥30 required)"
else
    echo "  ✗ FAIL (≥30 required, got $oxygen_count)"
fi
echo ""

echo "[8/10] Quality Gate 3: Inhaler devices..."
inhaler_count=$(grep -E "MDI|Turbuhaler|HandiHaler|Accuhaler|Respimat" data/osces/respiratory_50_osces_regenerated.json | wc -l)
echo "Inhaler device mentions found: $inhaler_count"
if [ $inhaler_count -ge 25 ]; then
    echo "  ✓ PASS (≥25 required)"
else
    echo "  ✗ FAIL (≥25 required, got $inhaler_count)"
fi
echo ""

echo "[8/10] Quality Gate 4: PBS codes..."
pbs_count=$(grep -o "PBS [0-9][0-9][0-9][0-9][A-Z]" data/osces/respiratory_50_osces_regenerated.json | wc -l)
echo "PBS codes found: $pbs_count"
if [ $pbs_count -ge 100 ]; then
    echo "  ✓ PASS (≥100 required)"
else
    echo "  ✗ FAIL (≥100 required, got $pbs_count)"
fi
echo ""

echo "[8/10] Quality Gate 5: Australian guidelines..."
guideline_count=$(grep -E "National Asthma Council|COPD-X|TSANZ|Lung Foundation Australia" data/osces/respiratory_50_osces_regenerated.json | wc -l)
echo "Australian guideline references found: $guideline_count"
if [ $guideline_count -ge 40 ]; then
    echo "  ✓ PASS (≥40 required)"
else
    echo "  ✗ FAIL (≥40 required, got $guideline_count)"
fi
echo ""

echo "[9/10] Spot checking 3 random OSCEs..."
python3 -c "
import json, random
with open('data/osces/respiratory_50_osces_regenerated.json') as f:
    data = json.load(f)
osces = data.get('osces', [])
samples = random.sample(osces, min(3, len(osces)))
for i, osce in enumerate(samples, 1):
    print(f'\n=== Sample {i} ===')
    print(f'OSCE Code: {osce.get(\"osce_code\", \"N/A\")}')
    print(f'Topic: {osce.get(\"topic\", \"N/A\")}')
    print(f'Difficulty: {osce.get(\"difficulty\", \"N/A\")}')
    print(f'Candidate instructions: {len(osce.get(\"candidate_instructions\", \"\"))} chars')
    print(f'Actor instructions: {len(osce.get(\"actor_instructions\", \"\"))} chars')
    print(f'Marking criteria: {len(osce.get(\"marking_criteria\", []))} items')
    print(f'Learning points: {len(osce.get(\"learning_points\", []))} items')
    print(f'Sample answer: {len(osce.get(\"sample_answer\", \"\"))} chars')
    print(f'References: {len(osce.get(\"references\", []))} items')

    # Check for specific content
    candidate = osce.get('candidate_instructions', '')
    if len(candidate) >= 500:
        print('  ✓ Candidate instructions meet length requirement')
    else:
        print(f'  ✗ Candidate instructions too short ({len(candidate)} < 500)')

    actor = osce.get('actor_instructions', '')
    if len(actor) >= 500:
        print('  ✓ Actor instructions meet length requirement')
    else:
        print(f'  ✗ Actor instructions too short ({len(actor)} < 500)')

    answer = osce.get('sample_answer', '')
    if len(answer) >= 1000:
        print('  ✓ Sample answer meets length requirement')
    else:
        print(f'  ✗ Sample answer too short ({len(answer)} < 1000)')

    criteria_count = len(osce.get('marking_criteria', []))
    if 10 <= criteria_count <= 15:
        print(f'  ✓ Marking criteria count appropriate ({criteria_count})')
    else:
        print(f'  ✗ Marking criteria count out of range ({criteria_count}, expected 10-15)')

    learning_count = len(osce.get('learning_points', []))
    if 5 <= learning_count <= 7:
        print(f'  ✓ Learning points count appropriate ({learning_count})')
    else:
        print(f'  ✗ Learning points count out of range ({learning_count}, expected 5-7)')
"
echo ""

echo "[10/10] Final summary..."
echo "=========================================="
echo "VALIDATION COMPLETE"
echo "=========================================="
echo ""
echo "All validation commands completed."
echo "Review results above to confirm all quality gates passed."
echo ""
echo "Output file: data/osces/respiratory_50_osces_regenerated.json"
echo ""
