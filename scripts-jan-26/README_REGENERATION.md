# Week 3 Cardiology MCQ Regeneration - Documentation

**Script**: `regenerate_week3_cardiology_with_claude.py`  
**Created**: 2026-01-27  
**Purpose**: Regenerate 200 placeholder cardiology MCQs with real clinical content using Claude (Anthropic API)

---

## Problem Statement

### What Happened (2026-01-26)

1. Generated 200 Week 3 Cardiology MCQs with **validated citations** (3 per MCQ, >0.70 confidence)
2. Used local LLMs (deepseek-r1:7b, llama3.1:70b) for content generation
3. **Result**: ALL 200 MCQs remained as placeholder templates

**Evidence**:
```json
{
  "question": {
    "scenario": "Clinical scenario for STEMI diagnosis ECG criteria",
    "stem": "Question stem about STEMI diagnosis ECG criteria?",
    "options": {
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }
  },
  "explanation": "Explanation for STEMI diagnosis ECG criteria",
  "references": [
    // ✅ 3 VALID CITATIONS with RAG confidence >0.70
  ]
}
```

### Root Cause (Constraint 4.2)

**Local 7B LLMs cannot handle complex medical MCQ generation.**

Complex MCQs require:
- Clinical realism (demographics, vitals, examination findings)
- Medical accuracy (dosages, contraindications, Australian guidelines)
- Complex reasoning (differential diagnosis, risk stratification)
- Structured output (valid JSON, 8+ fields, nested objects)
- Australian context (eTG, RANZCP, AMH, PBS, Australian spelling)
- Length (500-1000 tokens per MCQ)

**7B models fail at**: Multi-step reasoning + JSON formatting + medical domain knowledge simultaneously.

**System limitations**: 12 GB RAM → Cannot run 14B+ models (require 16 GB)

**Solution**: Use Claude (Anthropic API) for production-grade medical content generation.

---

## Script Architecture

### Agent OS Pattern

```
MCQRegenerationPM (Project Manager)
├── Load MCQs with validated citations (600 citations preserved)
├── Delegate to Claude (Anthropic API) for content generation
├── Validate no placeholders (Constraint 12)
├── Enforce Australian medical context (Constraint 1)
└── Save progress incrementally (every 10 MCQs)
```

### Key Features

1. **Preserves Validated Work**:
   - Keeps all 600 RAG-validated citations (3 per MCQ)
   - Maintains MCQ IDs, topic assignments, metadata structure

2. **Claude API Integration** (Constraint 4.2):
   - Uses `claude-sonnet-4-5-20250929` model
   - Handles complex medical reasoning + JSON output
   - 3000 token limit per response (enough for detailed MCQs)

3. **Australian Medical Context** (Constraint 1):
   - Drug names: paracetamol, salbutamol, adrenaline (NOT acetaminophen, albuterol, epinephrine)
   - Spelling: paediatric, anaesthesia, haemoglobin, oesophagus
   - Guidelines: Therapeutic Guidelines (eTG), AMH, PBS, AHPRA, RANZCP
   - Terminology: GP, Emergency Department, bulk-billed, Medicare

4. **Placeholder Validation** (Constraint 12):
   - Rejects any content with "Clinical scenario for...", "Option A", "Question about..."
   - Validates minimum content length (scenario ≥150 chars, explanation ≥250 chars)
   - Ensures patient demographics and Australian context present

5. **Incremental Progress**:
   - Creates timestamped backup before starting
   - Saves progress every 10 MCQs
   - Marks failed MCQs for manual review
   - Handles interruption gracefully (Ctrl+C)

---

## Usage

### Prerequisites

1. **Virtual Environment** (Constraint 4.0):
   ```bash
   source venv/bin/activate
   ```

2. **Anthropic Package**:
   ```bash
   pip install anthropic
   ```

3. **API Key**:
   ```bash
   export ANTHROPIC_API_KEY='your-key-here'
   ```
   
   Get your key from: https://console.anthropic.com/

### Run Script

```bash
cd /home/dev/Development/irStudy
source venv/bin/activate
export ANTHROPIC_API_KEY='your-key-here'
python scripts-jan-26/regenerate_week3_cardiology_with_claude.py
```

### Expected Output

```
======================================================================
WEEK 3 CARDIOLOGY MCQ REGENERATION - PROJECT MANAGER
======================================================================
LLM Provider: Claude (Anthropic API)
Model: claude-sonnet-4-5-20250929
Constraint 4.2: Local LLM bypass - using production-grade API
Constraint 1: Australian medical context enforced
Constraint 12: NO placeholder content allowed
======================================================================

📥 Loading MCQs from data/mcqs/week3_cardiology_200_mcqs.json
   Total MCQs: 200
   Placeholders: 200
   Citations per MCQ: 3
   ✓ File loaded successfully

💾 Creating backup at data/mcqs/week3_cardiology_200_mcqs_backup_20260127_123456.json
   ✓ Backup complete (456 KB)

======================================================================
STARTING REGENERATION
======================================================================

[1/200] Generating WEEK3-CARDIO-001
   Topic: Acute Coronary Syndrome → STEMI diagnosis ECG criteria
   Citations: 3 (confidence: 0.79)
   Calling Claude API...
   ✓ Generated real content (3.2s)
   Scenario: 287 chars
   Explanation: 512 chars

💾 Progress save: 10 regenerated, 0 failed, 0 skipped

[50/200] Generating WEEK3-CARDIO-050
...

======================================================================
REGENERATION COMPLETE
======================================================================
Total MCQs: 200
Regenerated: 200
Failed: 0
Skipped (already real): 0
Output: data/mcqs/week3_cardiology_200_mcqs.json
Backup: data/mcqs/week3_cardiology_200_mcqs_backup_20260127_123456.json

✅ All placeholders regenerated successfully!
```

---

## Testing Checklist

### Phase 1: Pre-Execution Validation

- [ ] **ANTHROPIC_API_KEY set**:
  ```bash
  echo $ANTHROPIC_API_KEY
  # Should output your key (not empty)
  ```

- [ ] **Virtual environment activated**:
  ```bash
  which python
  # Should output: /home/dev/Development/irStudy/venv/bin/python
  ```

- [ ] **Anthropic package installed**:
  ```bash
  pip list | grep anthropic
  # Should show: anthropic X.Y.Z
  ```

- [ ] **Input file exists**:
  ```bash
  ls -lh data/mcqs/week3_cardiology_200_mcqs.json
  # Should show file with size ~400-500 KB
  ```

### Phase 2: Test with 1-2 MCQs First

**Modify script temporarily**:
```python
# In regenerate_all() method, line ~356:
for i, mcq in enumerate(data['mcqs'][:2], 1):  # TEST: Only first 2 MCQs
```

Run and verify:
```bash
python scripts-jan-26/regenerate_week3_cardiology_with_claude.py
```

**Validate output**:
```bash
# Check generated content
head -100 data/mcqs/week3_cardiology_200_mcqs.json

# Look for:
# - Real patient demographics (age, sex, history)
# - Real clinical scenarios (NOT "Clinical scenario for...")
# - Real options (NOT "Option A", "Option B")
# - Australian spelling (paediatric, anaesthesia, haemoglobin)
# - Australian drug names (paracetamol, salbutamol, adrenaline)
```

### Phase 3: Validate No Placeholders

**Run validation check**:
```bash
# Search for placeholder patterns
grep -E "Clinical scenario for|Question stem about|Option A|Option B|Explanation for" \
  data/mcqs/week3_cardiology_200_mcqs.json

# Should return: NOTHING (exit code 1)
# If it finds matches: REGENERATION FAILED
```

### Phase 4: Verify Citations Preserved

**Check citations intact**:
```bash
# Count citations (should be 600 = 200 MCQs × 3 citations each)
grep -o '"rag_confidence"' data/mcqs/week3_cardiology_200_mcqs.json | wc -l
# Should output: 600
```

### Phase 5: Check Australian Context

**Validate Australian compliance**:
```bash
# Should find Australian terms
grep -i "paracetamol\|salbutamol\|adrenaline\|etg\|therapeutic guidelines" \
  data/mcqs/week3_cardiology_200_mcqs.json | head -10

# Should NOT find American terms
grep -i "acetaminophen\|albuterol\|epinephrine\|uptodate" \
  data/mcqs/week3_cardiology_200_mcqs.json
# Should return: NOTHING
```

### Phase 6: Full Regeneration (200 MCQs)

**Remove test limit** and run full regeneration:
```bash
python scripts-jan-26/regenerate_week3_cardiology_with_claude.py
```

**Expected duration**: ~10-15 minutes (200 MCQs × 3 seconds/MCQ + 2 sec rate limit)

**Expected cost**: ~$4-6 USD (200 MCQs × $0.02-0.03/MCQ)

---

## Cost Analysis

### Anthropic API Pricing

**Model**: `claude-sonnet-4-5-20250929`
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

### Per-MCQ Cost Estimate

**Input tokens** (per MCQ):
- Prompt template: ~800 tokens
- 3 RAG citations: ~1200 tokens (400 each)
- **Total input**: ~2000 tokens

**Output tokens** (per MCQ):
- Scenario: ~200 tokens
- Options: ~100 tokens
- Explanation: ~300 tokens
- **Total output**: ~600 tokens

**Cost per MCQ**:
- Input: 2000 tokens × $3.00 / 1M = $0.006
- Output: 600 tokens × $15.00 / 1M = $0.009
- **Total**: ~$0.015 per MCQ

### Total Cost (200 MCQs)

**Total cost**: 200 MCQs × $0.015 = **$3.00 USD**

**Justification** (per Constraint 4.2):
- Quality: 100% real content, no placeholders
- Compliance: Australian medical context enforced
- Citations: Preserved 600 validated citations
- Time: 10-15 minutes vs days of manual review
- **Value**: Acceptable cost for production-grade medical content

---

## Output Structure

### Example Generated MCQ

```json
{
  "id": "WEEK3-CARDIO-001",
  "specialty": "Cardiology",
  "topic": "Acute Coronary Syndrome",
  "subtopic": "STEMI diagnosis ECG criteria",
  "question": {
    "scenario": "A 62-year-old man with a history of hypertension and type 2 diabetes presents to the Emergency Department with sudden onset severe central chest pain radiating to his left arm. Pain started 45 minutes ago while gardening. He is diaphoretic and nauseous. Vital signs: BP 145/92 mmHg, HR 98 bpm, RR 20/min, SpO2 96% on room air, temperature 36.8°C. ECG shows 3mm ST elevation in leads II, III, and aVF with reciprocal ST depression in leads I and aVL. Troponin I pending.",
    "stem": "What is the most appropriate immediate management?",
    "options": {
      "A": "Administer aspirin 300 mg orally and commence GTN infusion 10 mcg/min",
      "B": "Arrange urgent coronary angiography within 90 minutes",
      "C": "Commence thrombolysis with tenecteplase 40 mg IV bolus immediately",
      "D": "Perform bedside echocardiography to assess LV function"
    }
  },
  "correct_answer": "A",
  "explanation": "Option A is correct. This patient presents with inferior STEMI (ST elevation in leads II, III, aVF with reciprocal changes). According to Therapeutic Guidelines: Cardiovascular (eTG Section 5.2.1), immediate management of STEMI includes: (1) Aspirin 300 mg orally unless contraindicated, (2) GTN for symptom relief and BP control if BP >90 mmHg systolic, (3) Pain relief with morphine, (4) Antiplatelet therapy. Option B (PCI) is the definitive reperfusion strategy but immediate medical therapy must be commenced first - door-to-balloon time target is <90 minutes but doesn't preclude initial medical management. Option C (thrombolysis) would only be considered if PCI unavailable within 120 minutes and no contraindications present - it's not first-line in settings with PCI capability. Option D (echo) delays time-critical treatment and is not part of initial STEMI management - echo can be performed after reperfusion therapy if needed.",
  "summary": "Inferior STEMI requires immediate aspirin + GTN per eTG Cardiovascular 5.2.1 before definitive PCI",
  "references": [
    {
      "title": "Ecg Book",
      "author": "Unknown Author",
      "year": "2020",
      "page": 112,
      "content": "ECG Rhythm Interpretation\nModule V\nAcute Myocardial Infarction\n...",
      "rag_confidence": 0.79,
      "source_type": "textbook"
    },
    // ... 2 more citations
  ],
  "regeneration_date": "2026-01-27T12:34:56.789012",
  "regeneration_method": "Claude (Anthropic API)",
  "regeneration_model": "claude-sonnet-4-5-20250929"
}
```

### Key Improvements from Placeholder

**Before** (placeholder):
```
"scenario": "Clinical scenario for STEMI diagnosis ECG criteria"
"stem": "Question stem about STEMI diagnosis ECG criteria?"
"options": {"A": "Option A", "B": "Option B", ...}
"explanation": "Explanation for STEMI diagnosis ECG criteria"
```

**After** (real content):
- Specific patient demographics (62-year-old man)
- Detailed vitals (BP, HR, RR, SpO2, temp)
- Timeline (45 minutes ago)
- Examination findings (diaphoretic, nauseous)
- Investigation results (ECG with specific findings)
- Real options (specific interventions, not "Option A")
- Evidence-based explanation citing eTG Section 5.2.1
- Australian context (Emergency Department, eTG guidelines)

---

## Troubleshooting

### Error: ANTHROPIC_API_KEY not set

**Symptom**:
```
❌ ERROR: ANTHROPIC_API_KEY environment variable not set
```

**Fix**:
```bash
export ANTHROPIC_API_KEY='your-key-here'
# Verify:
echo $ANTHROPIC_API_KEY
```

### Error: anthropic package not installed

**Symptom**:
```
❌ ERROR: anthropic package not installed
```

**Fix**:
```bash
source venv/bin/activate
pip install anthropic
```

### Error: Input file not found

**Symptom**:
```
FileNotFoundError: Input file not found: data/mcqs/week3_cardiology_200_mcqs.json
```

**Fix**:
```bash
# Check file exists
ls -l data/mcqs/week3_cardiology_200_mcqs.json

# If missing, check working directory
pwd
# Should be: /home/dev/Development/irStudy
```

### Error: JSON parse error from Claude

**Symptom**:
```
❌ JSON parse error: Expecting value: line 1 column 1 (char 0)
Response preview: Here is the MCQ in JSON format:...
```

**Cause**: Claude wrapped JSON in markdown code blocks

**Fix**: Script already handles this (lines 322-332) - if still occurring, check response format

### Warning: Rate limit exceeded

**Symptom**:
```
anthropic.RateLimitError: Rate limit exceeded
```

**Fix**: Script has 2-second delay between requests - if still occurring, increase delay:
```python
# Line 390:
time.sleep(5)  # Increase from 2 to 5 seconds
```

### Warning: Generated content has placeholders

**Symptom**:
```
❌ Generated content has placeholders - REJECTED
```

**Cause**: Claude occasionally returns template text despite instructions

**Fix**: Script automatically rejects and marks for manual review - failed MCQs saved with `regeneration_failed: true`

---

## Files Modified

### Input File
- `data/mcqs/week3_cardiology_200_mcqs.json` (read and updated in place)

### Output Files
- `data/mcqs/week3_cardiology_200_mcqs.json` (updated with real content)
- `data/mcqs/week3_cardiology_200_mcqs_backup_YYYYMMDD_HHMMSS.json` (timestamped backup)

### No Files Deleted
- Original file backed up before modification
- Validated citations preserved (600 citations)

---

## Constraints Compliance

### Constraint 4.2: LLM Integration
- ✅ Uses Claude (Anthropic API) for complex medical content
- ✅ Bypasses local 7B LLMs (proven to fail)
- ✅ Cost justified ($3-6 for 200 MCQs)

### Constraint 1: Australian Medical Context
- ✅ Australian drug names enforced (paracetamol, salbutamol, adrenaline)
- ✅ Australian spelling enforced (paediatric, anaesthesia, haemoglobin)
- ✅ Australian guidelines cited (eTG, AMH, PBS, RANZCP)
- ✅ Australian terminology used (GP, Emergency Department, bulk-billed)

### Constraint 12: No Placeholder Content
- ✅ Validates no placeholder patterns before saving
- ✅ Rejects "Clinical scenario for...", "Option A", etc.
- ✅ Ensures minimum content length
- ✅ Verifies patient demographics present

---

## Success Criteria

**All criteria MUST be met**:

- [ ] 200 MCQs regenerated with real clinical content
- [ ] 0 placeholder patterns detected
- [ ] 600 RAG citations preserved (3 per MCQ)
- [ ] Australian spelling used throughout
- [ ] Australian drug names used (no American equivalents)
- [ ] Australian guidelines cited (eTG, AMH, PBS)
- [ ] Each scenario has patient demographics (age, sex)
- [ ] Each explanation cites evidence and guidelines
- [ ] Backup file created before regeneration
- [ ] Progress saved every 10 MCQs

---

## Next Steps

After successful regeneration:

1. **Validate Output**:
   ```bash
   python scripts/validate_mcqs_qa003.py data/mcqs/week3_cardiology_200_mcqs.json
   ```

2. **Run Content Substance Validation**:
   ```bash
   scripts/validate_content_substance.sh data/mcqs/week3_cardiology_200_mcqs.json
   ```

3. **Commit Changes**:
   ```bash
   git add data/mcqs/week3_cardiology_200_mcqs.json
   git commit -m "feat: Regenerate Week 3 Cardiology MCQs with Claude (Anthropic API)

   - Replaced 200 placeholder MCQs with real clinical content
   - Preserved 600 RAG-validated citations (3 per MCQ)
   - Used Claude API per Constraint 4.2 (local 7B LLMs failed)
   - Enforced Australian medical context (Constraint 1)
   - Validated no placeholder content (Constraint 12)
   - Cost: ~$3-6 USD for production-grade medical content

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

4. **Update Documentation**:
   - Mark Week 3 Cardiology as 100% complete in planning docs
   - Update `CLAUDE.md` with successful regeneration pattern

---

**Script**: `scripts-jan-26/regenerate_week3_cardiology_with_claude.py`  
**Documentation**: `scripts-jan-26/README_REGENERATION.md`  
**Created**: 2026-01-27  
**Author**: Project Manager (Agent OS)  
**Constraint Compliance**: 4.2 (Claude API), 1 (Australian context), 12 (No placeholders)
