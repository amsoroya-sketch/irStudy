# Implementation Checklist: Psychiatry Error Prevention

**Date:** 2026-03-28
**Purpose:** Step-by-step checklist for developers implementing error prevention strategy
**Estimated Time:** 4-6 hours

---

## Phase 1: Understand the Problem (30 mins)

- [ ] Read evaluation summary: `EVALUATION_SESSION_SUMMARY_20260328.html`
- [ ] Review detailed examples: `SAFET_FIX_EXAMPLES_DETAILED.html`
- [ ] Understand root cause: Missing SAFE-T = 0% pass rate

**Key Takeaway:** SAFE-T suicide risk assessment is ZERO-TOLERANCE requirement

---

## Phase 2: Review New Constraints (1 hour)

- [ ] Read `constraints/15-psychiatry-mcq-requirements.md` (comprehensive)
- [ ] Understand Section 15.2: Zero-Tolerance Requirements
- [ ] Review Section 15.3: MCQ Generation Template
- [ ] Study Section 15.4: Content Generation Prompts (mandatory templates)

**Key Files:**
- `constraints/15-psychiatry-mcq-requirements.md` (NEW - 900+ lines)
- `PSYCHIATRY_ERROR_PREVENTION_STRATEGY.md` (NEW - prevention strategy)

---

## Phase 3: Set Up Validation Scripts (1 hour)

### Step 1: Create Validation Script

```bash
# Copy template from constraint file
cd /home/dev/Development/irStudy
mkdir -p scripts/validation
```

- [ ] Create `scripts/validate_psychiatry_mcq_generation.py`
  - Copy code from Section 15.5.1 of constraint file
  - Test with sample MCQ: `python scripts/validate_psychiatry_mcq_generation.py data/mcqs/temp_first_10_mcqs_for_evaluation.json`

### Step 2: Create Auto-Fix Script

- [ ] Create `scripts/auto_fix_psychiatry_mcqs.py`
  - Copy code from Section 15.6.1 of constraint file
  - Test with problematic MCQ: `python scripts/auto_fix_psychiatry_mcqs.py <file>`

### Step 3: Verify Scripts Work

```bash
# Test validation
python scripts/validate_psychiatry_mcq_generation.py data/mcqs/week1_all_100_unique_mcqs.json
# Should show: ✅ MCQ validation PASSED

# Test auto-fix on backup
cp data/mcqs/psychiatry_depression_day1.json data/mcqs/backups/
python scripts/auto_fix_psychiatry_mcqs.py data/mcqs/backups/psychiatry_depression_day1.json
# Should create: psychiatry_depression_day1_fixed.json
```

---

## Phase 4: Integrate with Content Generation (2 hours)

### Step 1: Identify Generation Entry Point

- [ ] Find your MCQ generation script
  - Likely: `clinical-content-prds/validation-system/batch1_persona_generator.py`
  - Or: Custom generation script

### Step 2: Add Constraint Loading

```python
class ContentGenerator:
    def __init__(self):
        # Add this
        self.constraints = self._load_constraints()

    def _load_constraints(self):
        """Load constraint files."""
        constraints = {}
        constraints['psychiatry'] = self._read_file('constraints/15-psychiatry-mcq-requirements.md')
        return constraints
```

- [ ] Update `__init__` method to load constraints
- [ ] Test: Verify constraint file loads successfully

### Step 3: Add Template Selection

```python
def generate_mcq(self, topic: str, specialty: str):
    """Generate MCQ with appropriate template."""

    # Add this
    if specialty == "psychiatry":
        if "depression" in topic.lower():
            template_section = "15.4.1"  # Depression template
        elif "suicide" in topic.lower():
            template_section = "15.4.2"  # Suicide risk template
        elif "psychosis" in topic.lower():
            template_section = "15.4.3"  # Psychosis template

        template = self._extract_template(self.constraints['psychiatry'], template_section)
        prompt = self._build_prompt_with_template(topic, template)
    else:
        prompt = self._build_standard_prompt(topic)

    # Continue with generation...
```

- [ ] Add template selection logic
- [ ] Test: Print generated prompt, verify SAFE-T mentioned

### Step 4: Add Pre-Validation

```python
# Before calling Claude API
from scripts.validate_psychiatry_mcq_generation import validate_generation_prompt

prompt = self._build_prompt_with_template(topic, template)

# Add this
if specialty == "psychiatry":
    valid, errors = validate_generation_prompt(prompt)
    if not valid:
        raise ValueError(f"Prompt validation failed: {errors}")

# Now safe to generate
mcq = self._call_claude_api(prompt)
```

- [ ] Import validation function
- [ ] Add pre-validation check
- [ ] Test: Trigger validation failure (remove SAFE-T from prompt), verify error

### Step 5: Add Post-Validation + Auto-Fix

```python
from scripts.validate_psychiatry_mcq_generation import validate_generated_mcq
from scripts.auto_fix_psychiatry_mcqs import fix_mcq

mcq = self._call_claude_api(prompt)

# Add this
if specialty == "psychiatry":
    valid, errors = validate_generated_mcq(mcq)
    if not valid:
        logger.warning(f"MCQ validation failed, applying auto-fixes: {errors}")
        mcq = fix_mcq(mcq)

        # Re-validate
        valid, errors = validate_generated_mcq(mcq)
        if not valid:
            raise ValueError(f"MCQ still invalid after auto-fix: {errors}")

return mcq
```

- [ ] Import validation + auto-fix functions
- [ ] Add post-validation check
- [ ] Test: Generate MCQ without SAFE-T, verify auto-fix triggers

---

## Phase 5: Update Existing MCQs (1 hour)

### Batch Update Script

```bash
#!/bin/bash
# File: scripts/batch_update_psychiatry_mcqs.sh

# Backup all psychiatry MCQ files
mkdir -p data/mcqs/backups/$(date +%Y%m%d)
cp data/mcqs/psychiatry_*.json data/mcqs/backups/$(date +%Y%m%d)/

# Apply fixes to each file
for file in data/mcqs/psychiatry_*.json; do
    echo "Fixing $file..."
    python scripts/auto_fix_psychiatry_mcqs.py "$file"

    # Validate
    fixed_file="${file%.json}_fixed.json"
    python scripts/validate_psychiatry_mcq_generation.py "$fixed_file"

    if [ $? -eq 0 ]; then
        echo "  ✅ Validation passed, replacing original"
        mv "$fixed_file" "$file"
    else
        echo "  ❌ Validation failed, keeping original"
    fi
done

echo "Batch update complete!"
```

- [ ] Create `scripts/batch_update_psychiatry_mcqs.sh`
- [ ] Make executable: `chmod +x scripts/batch_update_psychiatry_mcqs.sh`
- [ ] Run on test file first
- [ ] Run on all psychiatry files: `./scripts/batch_update_psychiatry_mcqs.sh`

---

## Phase 6: Update PRDs (30 mins)

### For Ralph Loop Execution

If you use Ralph loop for medical content generation:

- [ ] Update PRD template to reference Constraint 15
- [ ] Add validation step to PRD validations array
- [ ] Example: See Section 4.3 in `PSYCHIATRY_ERROR_PREVENTION_STRATEGY.md`

**PRD Update:**

```json
{
  "prd_id": "PRD-MCQ-PSYCHIATRY-001",
  "constraints": [
    "constraints/15-psychiatry-mcq-requirements.md"
  ],
  "prompt": "Generate psychiatry MCQs following Constraint 15. MANDATORY: Read constraints/15-psychiatry-mcq-requirements.md BEFORE starting.",
  "validations": [
    {
      "type": "test_suite",
      "description": "Psychiatry MCQ validation: 100% SAFE-T coverage",
      "blocking": true,
      "command": "python scripts/validate_psychiatry_mcq_generation.py {OUTPUT_DIR}/*.json"
    }
  ]
}
```

---

## Phase 7: Testing & Validation (1 hour)

### Test 1: Generate Single MCQ

```bash
# Generate a depression MCQ
python scripts/generate_single_mcq.py --topic "Depression - Moderate" --specialty psychiatry

# Expected: MCQ has SAFE-T as first key point
# Expected: Validation passes
# Expected: No auto-fixes needed (if prompt correct)
```

- [ ] Generate test MCQ
- [ ] Verify SAFE-T present
- [ ] Verify validation passes

### Test 2: Generate Batch of 10 MCQs

```bash
# Generate batch
python scripts/generate_batch_mcqs.py --topics psychiatry_topics.json --count 10

# Check all have SAFE-T
grep -c "SAFE-T" output/*.json
# Expected: 10 (100% coverage)

# Check no "Unknown" references
grep "Unknown" output/*.json
# Expected: No matches
```

- [ ] Generate batch
- [ ] Verify 100% SAFE-T coverage
- [ ] Verify 0 "Unknown" references

### Test 3: Run Full Evaluation

```bash
# Run evaluation on new batch
python evaluation-system/core/evaluation_orchestrator.py --file output/*.json --delegation-mode cli

# Expected results:
# - Pass rate: ≥90%
# - Mental Health Crisis Expert: ≥9.0/10
# - Gate 13: PASS
```

- [ ] Run full evaluation
- [ ] Verify metrics meet targets
- [ ] Document results

---

## Phase 8: Update Documentation (30 mins)

- [ ] Update `constraints/README.md` to reference Constraint 15
- [ ] Update `CLAUDE.md` (project instructions) with psychiatry requirements
- [ ] Update agent documentation if you have custom agents

**Add to CLAUDE.md:**

```markdown
## Psychiatry Content Requirements (CRITICAL)

**MANDATORY for ALL psychiatry MCQ generation:**
1. Read `constraints/15-psychiatry-mcq-requirements.md` BEFORE starting
2. Use templates from Section 15.4 (Depression, Suicide, Psychosis)
3. Validate EVERY MCQ: `scripts/validate_psychiatry_mcq_generation.py`
4. SAFE-T protocol is ZERO-TOLERANCE (automatic failure if missing)

**Quick check:**
- [ ] SAFE-T is first key point
- [ ] All 5 SAFE-T elements present
- [ ] Australian crisis contacts included
- [ ] References are NOT "Unknown"
```

---

## Phase 9: Deploy to Production (15 mins)

### Pre-Deployment Checklist

- [ ] All scripts tested and working
- [ ] Existing MCQs updated with SAFE-T fixes
- [ ] New generation pipeline includes validation
- [ ] Documentation updated
- [ ] Team trained on new requirements

### Deployment Steps

1. **Commit Changes**
   ```bash
   git add constraints/15-psychiatry-mcq-requirements.md
   git add scripts/validate_psychiatry_mcq_generation.py
   git add scripts/auto_fix_psychiatry_mcqs.py
   git add PSYCHIATRY_ERROR_PREVENTION_STRATEGY.md
   git commit -m "feat(psychiatry): Add SAFE-T zero-tolerance requirements and validation

   - Add Constraint 15: Psychiatry MCQ requirements
   - Add validation + auto-fix scripts
   - Update existing MCQs with SAFE-T protocol
   - Integrate with content generation pipeline

   Result: 0% → 90% pass rate on psychiatry MCQs
   Closes #XXX"
   ```

2. **Run Final Validation**
   ```bash
   # Validate all psychiatry MCQs
   for file in data/mcqs/psychiatry_*.json; do
       python scripts/validate_psychiatry_mcq_generation.py "$file"
   done
   ```

3. **Deploy**
   ```bash
   git push origin main
   ```

---

## Phase 10: Monitor & Maintain (Ongoing)

### Daily Monitoring

- [ ] Check generation logs for validation failures
- [ ] Track auto-fix rate (should be ≤20%)
- [ ] Monitor evaluation pass rates

### Weekly Review

- [ ] Review any manual fixes required
- [ ] Update templates if patterns emerge
- [ ] Share learnings with team

### Quarterly Review

- [ ] Review RANZCP guideline updates (Section 6.2 of prevention strategy)
- [ ] Update crisis contact numbers if changed
- [ ] Update Mental Health Act if legislation changed
- [ ] Re-validate sample of MCQs

---

## Success Criteria

**Implementation Complete When:**

- ✅ All validation scripts working
- ✅ Content generation pipeline integrated
- ✅ Existing MCQs updated
- ✅ Documentation updated
- ✅ Team trained
- ✅ Test generation passes validation
- ✅ Evaluation results: ≥90% pass rate

**Production Deployment Ready When:**

- ✅ 100 new MCQs generated with new system
- ✅ Pass rate ≥90% on evaluation
- ✅ Mental Health Crisis Expert ≥9.0/10
- ✅ Zero "Unknown" references
- ✅ 100% SAFE-T coverage

---

## Troubleshooting

### Issue: Validation script not found

```bash
# Solution: Check Python path
export PYTHONPATH=/home/dev/Development/irStudy:$PYTHONPATH
python scripts/validate_psychiatry_mcq_generation.py <file>
```

### Issue: Auto-fix not working

```bash
# Solution: Check MCQ structure
python -c "import json; print(json.load(open('file.json'))['explanation']['key_points'])"
# Verify key_points is array, not string
```

### Issue: Evaluation still failing

```bash
# Solution: Run validation first
python scripts/validate_psychiatry_mcq_generation.py <file>
# Fix any validation errors before running evaluation
```

### Issue: "Unknown" references still appearing

```bash
# Solution: Run auto-fix script
python scripts/auto_fix_psychiatry_mcqs.py <file>
# Auto-fix replaces "Unknown" with appropriate Australian guidelines
```

---

## Additional Resources

**Files Created:**
1. `constraints/15-psychiatry-mcq-requirements.md` (comprehensive constraint)
2. `PSYCHIATRY_ERROR_PREVENTION_STRATEGY.md` (prevention strategy)
3. `SAFET_VIOLATION_FIX_REPORT.md` (original fix documentation)
4. `EVALUATION_SESSION_SUMMARY_20260328.html` (evaluation results)
5. `SAFET_FIX_EXAMPLES_DETAILED.html` (before/after examples)
6. `evaluation-system/reports/SAFET_FIX_COMPARISON_REPORT.md` (comparison)
7. `evaluation-system/reports/EVALUATION_IMPROVEMENT_METRICS.md` (metrics)

**Key Scripts:**
1. `scripts/validate_psychiatry_mcq_generation.py` (pre/post validation)
2. `scripts/auto_fix_psychiatry_mcqs.py` (automatic fixes)
3. `scripts/batch_update_psychiatry_mcqs.sh` (batch processing)

**For Questions:**
- Review `PSYCHIATRY_ERROR_PREVENTION_STRATEGY.md` Section 5 (Validation & Testing)
- Check constraint file Section 15.8 (Enforcement Checklist)

---

**Estimated Total Time:** 4-6 hours
**Status:** ✅ Ready for Implementation
**Last Updated:** 2026-03-28
