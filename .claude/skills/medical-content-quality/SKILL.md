---
description: |
  Australian medical education content quality assurance for OSCE/MCQ generation.
  Ensures 100% RAG citation coverage, FRACP validation ≥8.0/10, and 13-gate QA compliance.
  Use when: generating medical content, validating clinical scenarios, reviewing OSCE cases
allowed-tools:
  - Read
  - Bash
  - Grep
user-invocable: true
effort: high
paths:
  - "data/**/*.json"
  - "scripts/**/*_validation.py"
  - "backend/**/*osce*.py"
---

# Medical Content Quality Skill

**Primary Reference**: `PROJECT_CONSTRAINTS.md` + `/constraints/14-ralph-medical-content-standards.md`

**Read constraints now**:
```bash
!`cat constraints/14-ralph-medical-content-standards.md 2>/dev/null || echo "File not found - check constraints/"`
```

## Critical Requirements (Zero Tolerance)

### 1. Australian Medical Context 🚨
```bash
# Quick validation - check for US spellings
!`grep -r "acetaminophen\|albuterol\|epinephrine" data/ --include="*.json" | wc -l || echo "0"`
```

**Must Use**:
- ✅ paracetamol (NOT acetaminophen)
- ✅ salbutamol (NOT albuterol)
- ✅ adrenaline (NOT epinephrine)
- ✅ eTG, PBS, AHPRA, AMH references

### 2. RAG Citations Required
Every clinical fact MUST have:
- qdrant_point_id (verified against Qdrant database)
- confidence ≥0.65 (≥0.70 for deployment)
- page numbers where applicable
- Exactly 3 citations per MCQ/OSCE

**Validation**:
```bash
!`python scripts/validate_rag_citations.py --min-confidence 0.65 data/osce/ 2>/dev/null || echo "Run validation script"`
```

### 3. No Placeholder Content
❌ **NEVER ALLOWED**:
- "Clinical scenario for..."
- "Option A", "Option B" templates
- "[INSERT X]" placeholders
- Generic "patient presents with..." without specifics

✅ **REQUIRED**:
- 100% real clinical content generated via Claude API
- Specific patient demographics (age, gender, background)
- Detailed clinical findings
- Evidence-based management

### 4. Quality Gates (ALL 13 MUST PASS)

```bash
# Run full 13-gate validation
!`python scripts/qa_validation_13_gates.py data/osce/batch_1/ 2>/dev/null || echo "Run QA validation"`
```

**Gates**:
1. ✅ JSON Compliance (17 required fields)
2. ✅ RAG Citations >0.65 confidence
3. ✅ FRACP Reviews ≥8.0/10
4. ✅ Clinical Accuracy (correct medications, dosing)
5. ✅ Australian Context (spelling, references, MBS/PBS)
6-7. ✅ Difficulty/Specialty Valid
8-10. ✅ Cultural Safety (Aboriginal/TSI, LGBTQIA+, CALD)
11-12. ✅ Security (zero credentials, zero PHI)
13. ✅ Educational Alignment (9-step history, SOCRATES, red flags)

## Pre-Flight Validation

**Before ANY medical content generation**:
```bash
# 1. Check Python venv activated
!`python --version && which python | grep venv || echo "⚠️  ACTIVATE venv: source venv/bin/activate"`

# 2. Run pre-flight checks
!`bash scripts/pre_flight_validation.sh 2>/dev/null || echo "Pre-flight script missing"`

# 3. Verify Claude API key (NEVER use local LLMs for MCQ/OSCE)
!`python -c "import os; print('✅ ANTHROPIC_API_KEY set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing API key')" 2>/dev/null`
```

## Common Anti-Patterns

### ❌ WRONG: Using local LLMs for content generation
```python
# DON'T DO THIS - local LLMs produce placeholders
client = ollama.Client()
response = client.generate(model="llama3:7b", prompt=mcq_prompt)
```

### ✅ CORRECT: Use Claude API
```python
# ALWAYS use Claude for medical content
import anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=4000,
    messages=[{"role": "user", "content": mcq_prompt}]
)
```

## Validation Checklist

Before committing medical content:

- [ ] Python venv activated
- [ ] No US drug names (grep check passes)
- [ ] All 13 quality gates pass
- [ ] 100% RAG citation coverage
- [ ] FRACP review ≥8.0/10
- [ ] No placeholder content
- [ ] Australian medical references only
- [ ] UTF-8 encoding for all JSON files

**Run full validation**:
```bash
!`bash medical-content-quality/scripts/validate-medical-content.sh`
```

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| RAG Citation Coverage | 100% | 100% ✅ |
| Deployment Readiness | ≥95% | 96.5% ✅ |
| Hallucinated Citations | 0% | 0% ✅ |
| Australian Sources | ≥60% | 66.1% ✅ |
| FRACP Review Score | ≥8.0/10 | 8.3/10 ✅ |

## References

- **See**: `constraints/1-medical-accuracy.md` - Australian standards
- **See**: `constraints/4-llm-integration.md` - Claude vs local LLMs
- **See**: `constraints/14-ralph-medical-content-standards.md` - Full quality gates
- **See**: `reference/quality-gates-checklist.md` - Detailed gate requirements
