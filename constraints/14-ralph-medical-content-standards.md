# Constraint 14: Ralph Medical Content Quality Standards

**Status**: **MANDATORY** - Auto-enforced in all medical content PRDs
**Created**: 2026-03-21
**Purpose**: Enforce RAG verification, citation quality, and 13-gate QA validation in Ralph loop execution
**Scope**: ALL medical content generation (patient personas, MCQs, OSCEs, study cards)

---

## 14.1 Overview: Automatic Quality Enforcement

### Why This Constraint Exists

**Problem**: Medical content generation could bypass quality gates if not explicitly enforced in PRDs
**Solution**: MANDATORY constraints that must be included in EVERY medical content PRD
**Enforcement**: Ralph Dashboard rejects PRDs that don't include these validations

### Zero-Tolerance Policies

| Violation | Action |
|-----------|--------|
| **Missing RAG citations** | ❌ PRD execution FAILS (cannot proceed) |
| **Hallucinated citations** (qdrant_point_id not found) | ❌ PRD execution FAILS |
| **Citation confidence <0.65** | ❌ PRD execution FAILS |
| **Missing 13-gate QA validation** | ❌ PRD marked BLOCKED |
| **Missing FRACP clinical validation** | ❌ PRD marked BLOCKED |
| **Placeholder content detected** | ❌ PRD execution FAILS |
| **US medical terminology** (acetaminophen) | ❌ PRD execution FAILS |
| **Hardcoded credentials** | ❌ PRD execution FAILS (security violation) |

---

## 14.2 Mandatory PRD Components for Medical Content

### Required Agent Assignment

**ONLY these agents can generate medical content:**

| Agent | File | Use Case |
|-------|------|----------|
| **clinical-documentation-expert** | `.claude/agents/clinical-documentation-expert.md` | Patient personas, clinical documentation |
| **history-taking-expert** | `.claude/agents/history-taking-expert.md` | Patient history components |
| **physical-examination-expert** | `.claude/agents/physical-examination-expert.md` | Physical examination scenarios |

**NEVER use** `general-purpose`, `react-frontend-developer`, or `python-backend-developer` for medical content generation.

### Required Skills (Minimum)

**ALL medical content PRDs MUST include these skills:**

```json
{
  "agent": {
    "name": "clinical-documentation-expert",
    "file": ".claude/agents/clinical-documentation-expert.md",
    "skills": [
      {
        "name": "rag-citation-verification",
        "file": ".claude/skills/rag-citation-verification/SKILL.md"
      },
      {
        "name": "australian-medical-terminology",
        "file": ".claude/skills/australian-medical-terminology/SKILL.md"
      },
      {
        "name": "fracp-clinical-validation",
        "file": ".claude/skills/fracp-clinical-validation/SKILL.md"
      }
    ]
  }
}
```

### Required Validations (Minimum 5)

**ALL medical content PRDs MUST include these validations:**

```json
{
  "validations": [
    {
      "type": "test_suite",
      "description": "QA validation: All content passes 13/13 gates",
      "blocking": true,
      "command": "cd /home/dev/Development/irStudy && python clinical-content-prds/validation-system/qa_validator.py --batch {OUTPUT_DIR}/*.json",
      "on_failure": "invoke_fix_loop"
    },
    {
      "type": "test_suite",
      "description": "FRACP clinical validation: All content scores ≥8.0/10",
      "blocking": true,
      "command": "cd /home/dev/Development/irStudy && python clinical-content-prds/validation-system/claude_validator.py --batch {OUTPUT_DIR}/*.json",
      "on_failure": "invoke_fix_loop"
    },
    {
      "type": "security_scan",
      "description": "No hardcoded credentials or PHI",
      "blocking": true,
      "command": "grep -r \"api_key\\|password\\|token\" {OUTPUT_DIR}/ && exit 1 || exit 0",
      "on_failure": "fail"
    },
    {
      "type": "code_coverage",
      "description": "RAG citation coverage: 100%",
      "blocking": true,
      "command": "cd /home/dev/Development/irStudy && python scripts/validate_rag_citations.py --input {OUTPUT_DIR}/*.json",
      "min_coverage": 100,
      "on_failure": "fail"
    },
    {
      "type": "integration_test",
      "description": "Database insertion: All content inserted successfully",
      "blocking": false,
      "command": "cd /home/dev/Development/irStudy && python scripts/insert_batch_content.py --input {OUTPUT_DIR}/*.json --verify",
      "on_failure": "warn"
    }
  ]
}
```

**NOTE**: Replace `{OUTPUT_DIR}` with actual output directory path in PRD.

### Required Prompt Structure

**ALL medical content PRDs MUST include these sections in prompt:**

```markdown
# Implementation Task: {Title}

## Requirements

### Medical Accuracy Requirements (CRITICAL)

1. **RAG Citation Verification (MANDATORY)**
   - ALL clinical facts MUST have RAG citations from eTG
   - Minimum confidence threshold: ≥0.65
   - Every citation MUST include `qdrant_point_id` (UUID)
   - NO hallucinated or fabricated citations tolerated

2. **Australian Clinical Guidelines (MANDATORY)**
   - Use Australian Therapeutic Guidelines (eTG) as primary source
   - Include MBS item numbers for investigations
   - Include PBS restrictions for medications
   - Use Australian drug names (paracetamol NOT acetaminophen)

3. **13-Gate QA Validation (MANDATORY)**
   - Run QA validator on EVERY item before saving
   - Deployment threshold: 13/13 gates PASS (100%)
   - Auto-fix common errors (terminology, MBS items)
   - Manual review if ≥3 gates fail

4. **FRACP Clinical Validation (MANDATORY)**
   - Use specialty-specific FRACP validator
   - Score threshold: ≥8.0/10
   - Auto-reject if clinical accuracy score <8.0

## Validation Checklist (Complete Before Returning)

**Agent MUST verify ALL of these before marking task complete:**

- [ ] All content items generated
- [ ] Run QA validator → 100% PASS
- [ ] RAG citations: 100% have qdrant_point_id
- [ ] Confidence: All citations ≥0.65
- [ ] Australian sources: ≥60%
- [ ] FRACP validation: All items score ≥8.0/10
- [ ] Cultural safety: Aboriginal/TSI, LGBTQIA+, CALD gates 100% PASS
- [ ] Security scan: 0 hardcoded credentials
- [ ] Database insertion: All rows inserted successfully
- [ ] Deployment readiness: 100%

## Anti-Patterns to Avoid

❌ **DON'T**: Generate citations without querying RAG
❌ **DON'T**: Use US medical terminology
❌ **DON'T**: Skip QA validation
❌ **DON'T**: Use placeholder content
```

### Required Context References

**ALL medical content PRDs MUST reference these documents:**

```json
{
  "context": {
    "documentation": [
      "constraints/01-medical-accuracy.md",
      "constraints/11-rag-citation-requirements.md",
      "constraints/12-content-generation-requirements.md",
      "constraints/14-ralph-medical-content-standards.md",
      "clinical-content-prds/COMPLETE_VALIDATION_SYSTEM_SUMMARY.md",
      "clinical-content-prds/CITATION_VERIFICATION_REPORT.md"
    ]
  }
}
```

---

## 14.3 Quality Gate Enforcement Flow

### Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Ralph Dashboard Loads Medical Content PRD          │
├─────────────────────────────────────────────────────────────┤
│ ✅ Verify agent is clinical expert (not general-purpose)   │
│ ✅ Verify skills include rag-citation-verification         │
│ ✅ Verify 5 required validations present                   │
│ ✅ Verify prompt includes medical accuracy requirements    │
│ ✅ Verify context references constraint files              │
│                                                             │
│ IF any check FAILS → REJECT PRD (cannot execute)           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼ IF ALL PASS
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Agent Executes with Constraints                    │
├─────────────────────────────────────────────────────────────┤
│ Agent reads:                                                │
│   - constraints/01-medical-accuracy.md                      │
│   - constraints/11-rag-citation-requirements.md             │
│   - constraints/12-content-generation-requirements.md       │
│   - constraints/14-ralph-medical-content-standards.md       │
│                                                             │
│ Agent generates content following constraints               │
│ Agent self-validates using checklist                        │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Post-Execution Validation (Ralph Dashboard)        │
├─────────────────────────────────────────────────────────────┤
│ Validation 1: QA Validator (13 gates)                      │
│   $ python qa_validator.py --batch output/*.json           │
│   IF FAIL → invoke_fix_loop (max 3 retries)                │
│                                                             │
│ Validation 2: FRACP Clinical Validator                     │
│   $ python claude_validator.py --batch output/*.json       │
│   IF FAIL → invoke_fix_loop (max 3 retries)                │
│                                                             │
│ Validation 3: Security Scan                                │
│   $ grep -r "api_key|password" output/                     │
│   IF FAIL → REJECT (security violation)                    │
│                                                             │
│ Validation 4: RAG Citation Coverage                        │
│   $ python validate_rag_citations.py --input output/*.json │
│   IF FAIL → REJECT (citation violation)                    │
│                                                             │
│ Validation 5: Database Insertion                           │
│   $ python insert_batch_content.py --verify                │
│   IF FAIL → WARN (manual review)                           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼ IF ALL PASS
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Deployment Decision                                │
├─────────────────────────────────────────────────────────────┤
│ IF all validations PASS:                                    │
│   ✅ Mark PRD as DONE                                       │
│   ✅ Content approved for deployment                        │
│   ✅ Update database: status='DONE', completedAt=NOW()      │
│                                                             │
│ ELSE IF validation FAILS:                                   │
│   ❌ Invoke fix loop (max 3 retries)                        │
│   ❌ If retries exhausted → Mark PRD as BLOCKED             │
│   ❌ Require manual review                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 14.4 RAG System Requirements

### Pre-Flight Validation (MANDATORY)

**BEFORE starting ANY medical content generation, verify RAG system is ready:**

```bash
# MANDATORY: Run this before ANY content generation PRD
./scripts/pre_flight_validation.sh

# Exit code 0 = SAFE to proceed
# Exit code 1 = DO NOT PROCEED (fix issues first)
```

**What it checks:**
1. ✅ Qdrant service health (http://localhost:6333/health)
2. ✅ RAG database metadata completeness (0% "Unknown" titles)
3. ✅ RAG citation quality (≥80% queries return valid citations)
4. ✅ Collection size (≥5,000 chunks minimum)

**Enforcement**: Ralph Dashboard runs this check before executing medical content PRDs.

### RAG Query Requirements

**ALL medical content generation MUST query RAG before generating content:**

```python
# MANDATORY: Query RAG first
from src.rag.query_engine import query_rag_system

rag_results = query_rag_system(
    query=f"{topic} Australian guidelines management",
    collection="etg",
    top_k=5,
    min_confidence=0.70  # Higher threshold for medical content
)

if not rag_results:
    raise ValueError(f"No RAG results for {topic} - cannot generate content")

# MANDATORY: Include RAG context in prompt
prompt = f"""
Generate {content_type} for {topic}.

RAG CONTEXT (MANDATORY TO USE):
{json.dumps(rag_results, indent=2)}

CRITICAL REQUIREMENTS:
- ONLY use citations from RAG CONTEXT above
- Each citation MUST include qdrant_point_id from RAG CONTEXT
- Confidence threshold: ≥0.70
"""
```

### Citation Verification (MANDATORY)

**ALL citations MUST be verified against Qdrant database:**

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# For each citation in generated content
for citation in content["citations"]:
    point_id = citation["qdrant_point_id"]

    # Verify point ID exists in Qdrant
    result = client.retrieve(
        collection_name="etg",
        ids=[point_id]
    )

    if not result:
        raise ValidationError(
            f"Citation {point_id} not found in Qdrant - hallucination detected"
        )

    # Verify metadata matches
    if result[0].payload["page"] != citation["page"]:
        raise ValidationError(
            f"Citation page mismatch: {citation['page']} != {result[0].payload['page']}"
        )
```

---

## 14.5 13-Gate QA Validation System

### Quality Gates (ALL MUST PASS)

| Gate | Check | Implementation | Blocking |
|------|-------|----------------|----------|
| **Gate 1** | JSON Compliance (17 fields) | `_gate_1_json_compliance()` | ✅ Yes |
| **Gate 2** | RAG Citations >0.65 | `_gate_2_rag_citations()` | ✅ Yes |
| **Gate 3** | ≥2 FRACP Reviews (≥8.0/10) | `_gate_3_fracp_reviews()` | ✅ Yes |
| **Gate 4** | Clinical Accuracy | `_gate_4_clinical_accuracy()` | ✅ Yes |
| **Gate 5** | Australian Context | `_gate_5_australian_context()` | ✅ Yes |
| **Gate 6** | Difficulty Appropriate | `_gate_6_difficulty()` | ✅ Yes |
| **Gate 7** | Specialty Valid | `_gate_7_specialty()` | ✅ Yes |
| **Gate 8** | Aboriginal/TSI Safety | `_gate_8_aboriginal()` | ⚠️ If applicable |
| **Gate 9** | LGBTQIA+ Safety | `_gate_9_lgbtqia()` | ⚠️ If applicable |
| **Gate 10** | CALD Safety | `_gate_10_cald()` | ⚠️ If applicable |
| **Gate 11** | Zero Credentials | `_gate_11_security()` | ✅ Yes |
| **Gate 12** | Zero PHI Violations | `_gate_12_phi()` | ✅ Yes |
| **Gate 13** | Educational Alignment | `_gate_13_education()` | ✅ Yes |

**Pass Threshold**: 13/13 gates (100% for applicable gates)
**Deployment Threshold**: 100% deployment readiness

### QA Validator Execution

```bash
# Single item validation
python clinical-content-prds/validation-system/qa_validator.py \
  --input output/cardiology_001_stemi.json

# Batch validation
python clinical-content-prds/validation-system/qa_validator.py \
  --batch output/*.json

# Expected output:
# ✅ Gates Passed: 13/13
# ✅ Gates Failed: 0
# ✅ Deployment Readiness: 100.0%
# ✅ Recommendation: APPROVED FOR DEPLOYMENT
```

---

## 14.6 FRACP Clinical Validation

### Specialty-Specific Validators

| Validator | Specialty | Use For |
|-----------|-----------|---------|
| **FRACP-VALIDATOR-001** | Cardiology | Cardiology personas/MCQs |
| **FRACP-VALIDATOR-002** | Emergency | Emergency medicine content |
| **FRACP-VALIDATOR-003** | General Practice | GP content |
| **FRACP-VALIDATOR-004** | Pediatrics | Pediatrics content |
| **FRACP-VALIDATOR-005** | ObGyn | ObGyn content |
| **FRACP-VALIDATOR-006** | Surgery | Surgical content |
| **FRACP-VALIDATOR-007** | Psychiatry | Psychiatry content |
| **FRACP-VALIDATOR-008** | Respiratory | Respiratory content |
| **FRACP-VALIDATOR-009** | Neurology | Neurology content |
| **FRACP-VALIDATOR-010** | Infectious Diseases | ID content |

### Scoring Criteria (8 criteria, 0-10 points)

1. **Diagnosis accuracy** (0-2 points) - Correct diagnosis, ICD-10 code
2. **Management plan appropriateness** (0-2 points) - Evidence-based management
3. **Medication dosing correctness** (0-1 point) - Correct doses, routes, timing
4. **Investigation ordering** (0-1 point) - Appropriate tests ordered
5. **Australian guideline alignment** (0-1 point) - eTG, RACGP, RANZCOG references
6. **Red flags identified** (0-1 point) - Appropriate red flags listed
7. **Referral pathways** (0-1 point) - Correct referral decisions
8. **Educational value** (0-1 point) - Learning objectives met

**Pass Threshold**: ≥8.0/10

### FRACP Validator Execution

```python
from clinical-content-prds.validation-system.claude_validator import FRACPValidator

validator = FRACPValidator(api_key=os.getenv("ANTHROPIC_API_KEY"))

result = validator.validate_persona(
    persona_json=content,
    validator_id="FRACP-VALIDATOR-001"  # Cardiology
)

if result["clinical_score"] < 8.0:
    raise ValidationError(
        f"Clinical score too low: {result['clinical_score']}/10"
    )
```

---

## 14.7 Auto-Fix Common Errors

### Fixable Errors (Auto-Corrected)

| Error Type | Auto-Fix | Example |
|------------|----------|---------|
| **US terminology** | Replace with Australian | acetaminophen → paracetamol |
| **Missing MBS items** | Add MBS item numbers | Add "MBS 721" for Cycle of Care |
| **Missing PBS restrictions** | Add PBS details | Add "PBS restricted" |
| **Missing SOCRATES** | Add SOCRATES template | Add pain assessment |
| **Missing 9-step history** | Add history structure | Add systematic history |

### Non-Fixable Errors (Require Regeneration)

| Error Type | Action | Reason |
|------------|--------|--------|
| **Hallucinated citations** | REJECT | Cannot auto-fix fabricated data |
| **Low confidence (<0.65)** | REJECT | Cannot improve RAG quality automatically |
| **Clinical inaccuracies** | REJECT | Cannot auto-correct medical errors |
| **Dangerous medications** | REJECT | Safety-critical, requires expert review |

---

## 14.8 Enforcement Checklist for PRD Authors

**Before creating a medical content PRD, ensure:**

- [ ] Agent is clinical expert (clinical-documentation-expert, history-taking-expert, or physical-examination-expert)
- [ ] Skills include: rag-citation-verification, australian-medical-terminology, fracp-clinical-validation
- [ ] Validations include all 5 required validations (QA, FRACP, security, RAG coverage, database)
- [ ] Prompt includes Medical Accuracy Requirements section
- [ ] Prompt includes Validation Checklist section
- [ ] Prompt includes Anti-Patterns section
- [ ] Context references constraint files (14 files minimum)
- [ ] PRD has risk_level: "HIGH" (medical content is always high risk)
- [ ] PRD has priority: "P0" or "P1" (medical content is high priority)

**Ralph Dashboard will REJECT PRDs that don't meet these requirements.**

---

## 14.9 Example Medical Content PRD Template

**See**: `/home/dev/Development/irStudy/production-launch-prds/.ralph/examples/PRD-CONTENT-001-CARDIOLOGY-STEMI-PERSONAS.json`

**Key Sections:**
1. Agent: clinical-documentation-expert with 3 required skills
2. Prompt: Includes Medical Accuracy Requirements, 13-Gate QA Validation, FRACP Clinical Validation
3. Validations: All 5 required validations with exact commands
4. Context: References all constraint files
5. Risk Level: HIGH
6. Priority: P0 or P1

---

## 14.10 Monitoring and Metrics

### Quality Metrics (Tracked Per Batch)

| Metric | Target | Current (Batch 1) |
|--------|--------|-------------------|
| **Deployment Readiness** | 100% | 96.5% |
| **RAG Citation Coverage** | 100% | 100% |
| **Average Confidence** | ≥0.70 | 0.75 |
| **Australian Sources** | ≥60% | 66.1% |
| **QA Gate Pass Rate** | 100% | 96-100% (per gate) |
| **FRACP Pass Rate** | ≥90% | 96% |
| **Auto-Fix Success Rate** | ≥80% | 92% |

### Violation Tracking

**All violations logged and tracked:**

```json
{
  "prd_id": "PRD-CONTENT-001",
  "violation_type": "hallucinated_citation",
  "severity": "CRITICAL",
  "details": "Citation qdrant_point_id not found in database",
  "action_taken": "PRD execution FAILED",
  "timestamp": "2026-03-21T10:30:00Z"
}
```

**Monthly review**: Analyze violations to improve constraints and validation

---

## 14.11 References

### Constraint Files

- `constraints/01-medical-accuracy.md` - Australian medical standards
- `constraints/11-rag-citation-requirements.md` - RAG citation requirements
- `constraints/12-content-generation-requirements.md` - LLM content generation requirements
- `constraints/14-ralph-medical-content-standards.md` - This file

### Validation System

- `clinical-content-prds/validation-system/qa_validator.py` - 13-gate QA validator
- `clinical-content-prds/validation-system/claude_validator.py` - FRACP clinical validators
- `scripts/validate_rag_citations.py` - RAG citation verifier
- `scripts/pre_flight_validation.sh` - Pre-flight checks

### Documentation

- `clinical-content-prds/COMPLETE_VALIDATION_SYSTEM_SUMMARY.md` - Full validation system
- `clinical-content-prds/CITATION_VERIFICATION_REPORT.md` - Citation quality metrics
- `production-launch-prds/.ralph/MEDICAL_CONTENT_QUALITY_CONTROL_GUIDE.md` - Quality control guide

---

**Document Version**: 1.0.0
**Last Updated**: 2026-03-21
**Status**: MANDATORY for all medical content PRDs
**Enforcement**: Ralph Dashboard + Quality Gates
