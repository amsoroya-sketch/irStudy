# Respiratory OSCE Regeneration - Execution Guide

## Overview
This guide provides step-by-step instructions for regenerating 50 respiratory OSCEs with 100% real clinical content, replacing all placeholder templates.

**Estimated Time:** 100-150 minutes (50 OSCEs × 2-3 minutes each)

## Prerequisites Checklist

- [ ] Input file exists: `data/osces/respiratory_50_osces.json`
- [ ] Script exists: `scripts/regenerate_respiratory_osces.py`
- [ ] Placeholder detection script exists: `scripts/detect_placeholder_content.py`
- [ ] Claude API key configured (check env or config)
- [ ] Python 3.8+ installed
- [ ] Required Python packages installed (anthropic, json, etc.)

## Execution Steps

### Step 1: Pre-Flight Check

Run the validation script to ensure all prerequisites are met:

```bash
cd /home/dev/Development/irStudy

# Make script executable
chmod +x run_respiratory_regeneration.sh

# Check current baseline
python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces.json
```

**Expected Output:**
- Placeholder rate: 100% (50/50 OSCEs with templates)

### Step 2: Execute Regeneration

**IMPORTANT:** This will take 100-150 minutes. Run in a terminal that won't timeout:

```bash
# Option 1: Run with full validation
./run_respiratory_regeneration.sh

# Option 2: Run manually if script fails
python3 scripts/regenerate_respiratory_osces.py \
  data/osces/respiratory_50_osces.json \
  data/osces/respiratory_50_osces_regenerated.json
```

### Step 3: Monitor Progress

Open a second terminal and monitor progress:

```bash
cd /home/dev/Development/irStudy

# Watch file size grow (should increase from ~100KB to ~500KB+)
watch -n 30 'ls -lh data/osces/respiratory_50_osces_regenerated.json 2>/dev/null || echo "Not created yet"'

# Check logs if available
tail -f respiratory_regeneration.log 2>/dev/null || echo "No log file"
```

### Step 4: Post-Execution Validation

After regeneration completes, run all quality gates:

```bash
cd /home/dev/Development/irStudy

# Gate 1: File created
ls -lh data/osces/respiratory_50_osces_regenerated.json

# Gate 2: JSON valid
python3 -m json.tool data/osces/respiratory_50_osces_regenerated.json > /dev/null && echo "✓ JSON valid"

# Gate 3: Count OSCEs
python3 -c "import json; data = json.load(open('data/osces/respiratory_50_osces_regenerated.json')); print(f'OSCEs: {len(data.get(\"osces\", []))}')"

# Gate 4: Placeholder rate (CRITICAL)
python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces_regenerated.json

# Gate 5: Spirometry values
echo "Spirometry mentions:"
grep -o "FEV1.*L.*predicted" data/osces/respiratory_50_osces_regenerated.json | wc -l
echo "Expected: ≥40"

# Gate 6: Oxygen targets
echo "Oxygen target specifications:"
grep -E "88-92%|94-98%" data/osces/respiratory_50_osces_regenerated.json | wc -l
echo "Expected: ≥30"

# Gate 7: Inhaler devices
echo "Inhaler device mentions:"
grep -E "MDI|Turbuhaler|HandiHaler|Accuhaler|Respimat" data/osces/respiratory_50_osces_regenerated.json | wc -l
echo "Expected: ≥25"

# Gate 8: PBS codes
echo "PBS codes:"
grep -o "PBS [0-9][0-9][0-9][0-9][A-Z]" data/osces/respiratory_50_osces_regenerated.json | wc -l
echo "Expected: ≥100"

# Gate 9: Australian guidelines
echo "Australian guideline references:"
grep -E "National Asthma Council|COPD-X|TSANZ|Lung Foundation Australia" data/osces/respiratory_50_osces_regenerated.json | wc -l
echo "Expected: ≥40"
```

### Step 5: Spot Check Random OSCEs

```bash
python3 -c "
import json, random
with open('data/osces/respiratory_50_osces_regenerated.json') as f:
    data = json.load(f)
osces = data.get('osces', [])
samples = random.sample(osces, 3)
for i, osce in enumerate(samples, 1):
    print(f'\n=== Sample {i} ===')
    print(f'Code: {osce.get(\"osce_code\")}')
    print(f'Topic: {osce.get(\"topic\")}')
    print(f'Candidate: {len(osce.get(\"candidate_instructions\", \"\"))} chars')
    print(f'Actor: {len(osce.get(\"actor_instructions\", \"\"))} chars')
    print(f'Marking: {len(osce.get(\"marking_criteria\", []))} items')
    print(f'Sample answer: {len(osce.get(\"sample_answer\", \"\"))} chars')
    # Show first 200 chars of candidate instructions
    print(f'\nPreview: {osce.get(\"candidate_instructions\", \"\")[:200]}...')
"
```

## Quality Gates - Success Criteria

All of the following MUST pass:

### Critical Gates (ZERO TOLERANCE)

- [ ] **Placeholder Rate: 0%** (was 100%)
  - NO generic templates like "A patient presents for respiratory assessment"
  - NO placeholder text like "Clinical history relevant to..."

- [ ] **Oxygen Targets: ≥30 specifications**
  - COPD: 88-92% (avoid CO2 retention)
  - Non-COPD: 94-98%
  - This is LIFE-CRITICAL, cannot be generic

### High Priority Gates

- [ ] **Spirometry Values: ≥40 OSCEs**
  - Specific FEV1/FVC values with % predicted
  - Pattern identification (obstruction/restriction)

- [ ] **PBS Codes: ≥100 total**
  - All medications must have doses + PBS codes
  - Example: "Salbutamol 5mg nebulized QID, PBS 8333L"

- [ ] **Australian Guidelines: ≥40 references**
  - National Asthma Council Australia
  - COPD-X Plan
  - TSANZ guidelines
  - NOT US-only sources (GOLD without Australian context)

### Standard Gates

- [ ] **Inhaler Devices: ≥25 specifications**
  - Specific devices (MDI, Turbuhaler, HandiHaler, etc.)
  - Technique described

- [ ] **File Count: Exactly 50 OSCEs**

- [ ] **JSON Valid: No syntax errors**

- [ ] **Structure Complete: All 17 required fields**
  - osce_id, osce_code, topic, subtopic, difficulty
  - candidate_instructions (≥500 chars)
  - actor_instructions (≥500 chars)
  - marking_criteria (10-15 items)
  - sample_answer (≥1000 chars)
  - learning_points (5-7 items)
  - estimated_duration (8-10 minutes)
  - references (≥2 Australian sources)

## Troubleshooting

### Issue: Script fails with API error

```bash
# Check Claude API key
echo $ANTHROPIC_API_KEY

# Check rate limits (should be <90 req/min)
# Wait 1 minute and retry
```

### Issue: Placeholder rate still high

```bash
# Identify which OSCEs have placeholders
python3 scripts/detect_placeholder_content.py \
  data/osces/respiratory_50_osces_regenerated.json \
  --verbose

# Review specific OSCE codes that failed
```

### Issue: Quality gates fail

```bash
# For spirometry failures:
grep -B5 -A5 "FEV1" data/osces/respiratory_50_osces_regenerated.json | head -50

# For PBS code failures:
grep -B5 -A5 "PBS" data/osces/respiratory_50_osces_regenerated.json | head -50

# For oxygen target failures:
grep -B5 -A5 "88-92\|94-98" data/osces/respiratory_50_osces_regenerated.json | head -50
```

## Expected Outcomes

### Before Regeneration
- File: `respiratory_50_osces.json`
- Placeholder rate: 100%
- Content: Generic templates
- Example: "A patient presents for respiratory assessment"

### After Regeneration
- File: `respiratory_50_osces_regenerated.json`
- Placeholder rate: 0%
- Content: Specific clinical scenarios
- Example: "Mrs. Sarah Chen, 58-year-old, presents with progressive dyspnea over 3 days. She has known severe COPD (FEV1 35% predicted, on home oxygen 2L/min nocturnal). Current vitals: RR 28, SpO2 86% on room air, HR 112. Target SpO2 88-92% (COPD patient)..."

## Final Checklist

Before marking work complete:

- [ ] All 10 validation steps completed
- [ ] All 8 quality gates passed
- [ ] 3 random OSCEs spot-checked and meet standards
- [ ] Placeholder rate confirmed at 0%
- [ ] File backed up if satisfied with results
- [ ] Documentation updated with results

## Backup Command

Once satisfied with results:

```bash
# Backup original
cp data/osces/respiratory_50_osces.json \
   data/osces/respiratory_50_osces_original_backup_$(date +%Y%m%d).json

# Replace original with regenerated
cp data/osces/respiratory_50_osces_regenerated.json \
   data/osces/respiratory_50_osces.json

echo "✓ Regeneration complete and deployed"
```

## Contact for Issues

If any quality gates fail or issues arise:
1. Document which gate(s) failed
2. Provide sample OSCEs showing the issue
3. Run verbose placeholder detection
4. Check API logs for errors

---

**Last Updated:** 2026-03-29
**Script Version:** 1.0
**Expected Duration:** 100-150 minutes
