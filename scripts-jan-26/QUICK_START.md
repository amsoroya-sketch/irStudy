# Quick Start - MCQ Regeneration

**Goal**: Regenerate 200 placeholder cardiology MCQs with real clinical content using Claude (Anthropic API)

---

## Prerequisites (5 minutes)

### 1. Get Anthropic API Key
- Visit: https://console.anthropic.com/
- Create account or sign in
- Navigate to API Keys
- Create new key
- Copy key (starts with `sk-ant-...`)

### 2. Install Dependencies
```bash
cd /home/dev/Development/irStudy
source venv/bin/activate
pip install anthropic
```

### 3. Set API Key
```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# Verify:
echo $ANTHROPIC_API_KEY
# Should output your key
```

---

## Test Run (2-3 minutes)

Test with 2 MCQs first:

### 1. Edit Script Temporarily
```bash
# Open script
nano scripts-jan-26/regenerate_week3_cardiology_with_claude.py

# Find line ~356 (in regenerate_all method):
for i, mcq in enumerate(data['mcqs'], 1):

# Change to:
for i, mcq in enumerate(data['mcqs'][:2], 1):  # TEST: First 2 only

# Save and exit (Ctrl+X, Y, Enter)
```

### 2. Run Test
```bash
python scripts-jan-26/regenerate_week3_cardiology_with_claude.py
```

### 3. Verify Output
```bash
# Check first MCQ has real content
head -100 data/mcqs/week3_cardiology_200_mcqs.json | grep -A 5 "scenario"

# Should see real patient scenario like:
# "scenario": "A 62-year-old man with history of hypertension..."

# NOT placeholder like:
# "scenario": "Clinical scenario for STEMI..."
```

### 4. Run Validation
```bash
python scripts-jan-26/validate_regenerated_mcqs.py data/mcqs/week3_cardiology_200_mcqs.json

# Should output:
# ✅ ALL CHECKS PASSED
```

---

## Full Run (10-15 minutes)

If test successful, run full regeneration:

### 1. Undo Test Limit
```bash
# Open script again
nano scripts-jan-26/regenerate_week3_cardiology_with_claude.py

# Change back to:
for i, mcq in enumerate(data['mcqs'], 1):  # Full 200 MCQs

# Save and exit
```

### 2. Run Full Regeneration
```bash
python scripts-jan-26/regenerate_week3_cardiology_with_claude.py
```

**Expected duration**: 10-15 minutes (200 MCQs × 3 seconds + 2 sec rate limit)

**Expected cost**: $3-6 USD

### 3. Monitor Progress
The script saves every 10 MCQs, so you'll see:
```
[1/200] Generating WEEK3-CARDIO-001
   ✓ Generated real content (3.2s)

[10/200] Generating WEEK3-CARDIO-010
   ✓ Generated real content (2.8s)
💾 Progress save: 10 regenerated, 0 failed, 0 skipped

[20/200] Generating WEEK3-CARDIO-020
...
```

### 4. Handle Interruption
If you need to stop (Ctrl+C):
- Progress is saved automatically
- Backup file preserved
- Re-run script to continue from where it stopped

---

## Validation (2 minutes)

After regeneration completes:

```bash
# Run full validation
python scripts-jan-26/validate_regenerated_mcqs.py data/mcqs/week3_cardiology_200_mcqs.json

# Expected output:
======================================================================
VALIDATION SUMMARY
======================================================================
✅ ALL CHECKS PASSED
   File: data/mcqs/week3_cardiology_200_mcqs.json
   MCQs: 200
   Constraints: 1 (Australian), 12 (No placeholders)
```

---

## Verify Results

### Check Statistics
```bash
# Count total MCQs
jq '.mcqs | length' data/mcqs/week3_cardiology_200_mcqs.json
# Should output: 200

# Count citations (should be 600 = 200 × 3)
grep -c '"rag_confidence"' data/mcqs/week3_cardiology_200_mcqs.json
# Should output: 600

# Check for placeholders (should find NONE)
grep -c "Clinical scenario for" data/mcqs/week3_cardiology_200_mcqs.json
# Should output: 0

# Check Australian terms (should find many)
grep -c "paracetamol\|salbutamol\|adrenaline" data/mcqs/week3_cardiology_200_mcqs.json
# Should output: >0
```

### Manual Spot Check
```bash
# View first MCQ
head -100 data/mcqs/week3_cardiology_200_mcqs.json | less

# Look for:
# ✅ Real patient demographics (age, sex)
# ✅ Real clinical presentation
# ✅ Real answer options (NOT "Option A")
# ✅ Australian spelling (paediatric, anaesthesia)
```

---

## Commit Changes

If all validation passes:

```bash
git add data/mcqs/week3_cardiology_200_mcqs.json
git commit -m "feat: Regenerate Week 3 Cardiology MCQs with Claude (Anthropic API)

- Replaced 200 placeholder MCQs with real clinical content
- Preserved 600 RAG-validated citations (3 per MCQ)
- Used Claude API per Constraint 4.2 (local 7B LLMs failed)
- Enforced Australian medical context (Constraint 1)
- Validated no placeholder content (Constraint 12)
- Cost: ~\$3-6 USD for production-grade medical content

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Troubleshooting

### Error: ANTHROPIC_API_KEY not set
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### Error: anthropic package not installed
```bash
source venv/bin/activate
pip install anthropic
```

### Error: Input file not found
```bash
# Check you're in project root
pwd
# Should output: /home/dev/Development/irStudy

# Check file exists
ls -l data/mcqs/week3_cardiology_200_mcqs.json
```

### Error: Rate limit exceeded
Script has 2-second delay. If still rate limited, increase delay:
```python
# Line 390 in script:
time.sleep(5)  # Increase from 2 to 5 seconds
```

---

## Files Created

- `scripts-jan-26/regenerate_week3_cardiology_with_claude.py` - Main script
- `scripts-jan-26/validate_regenerated_mcqs.py` - Validation
- `scripts-jan-26/README_REGENERATION.md` - Full documentation
- `scripts-jan-26/DELIVERABLES_SUMMARY.md` - Summary
- `scripts-jan-26/QUICK_START.md` - This file
- `data/mcqs/week3_cardiology_200_mcqs_backup_*.json` - Auto-backup

---

## Summary

1. Get API key (5 min)
2. Test with 2 MCQs (2 min)
3. Run full regeneration (10-15 min)
4. Validate output (2 min)
5. Commit changes (1 min)

**Total time**: ~20-25 minutes  
**Total cost**: ~$3-6 USD

**Result**: 200 production-grade cardiology MCQs with real clinical content, Australian medical context, and zero placeholders.

---

**Need help?** See `README_REGENERATION.md` for full documentation.
