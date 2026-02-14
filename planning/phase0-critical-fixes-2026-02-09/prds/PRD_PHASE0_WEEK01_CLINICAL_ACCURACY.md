# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: PHASE0_WEEK01 - Clinical Accuracy Review & AMC Compliance (3-5 days)

**EXECUTE NOW**:

Read all clinical review materials and prepare documentation for Clinical Advisor approval. DO NOT wait for approval - prepare ALL materials NOW.

**DO NOT**:
- ❌ Ask "Would you like me to proceed?"
- ❌ Ask "Should I start with the rubric?"
- ❌ Wait for Clinical Advisor approval before preparing materials
- ❌ Skip any sections or ask for clarification

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📊 Metadata

- **Phase:** 0 (Critical Fixes)
- **Week:** 0.1
- **Duration:** 3-5 days
- **Priority:** P0-Critical (BLOCKING Phase 1)
- **Dependencies:** None
- **Owner:** Clinical Education Specialist + Clinical Advisor (approval)
- **Status:** 🔴 Not Started - BLOCKING

---

## 🎯 Objectives

1. **Expand AMC 15-mark rubric** with official citations and detailed scoring criteria
2. **Create 3 additional diverse clinical scenarios** (total 6: existing + 5 new)
3. **Implement RAG validation specification** with Australian source filtering
4. **Define Golden Dataset methodology** for 200 expert-validated scenarios
5. **Add Australian healthcare context** (Medicare, PBS, AHPRA standards)
6. **Obtain Clinical Advisor approval** for all clinical content

---

## 🚨 Constraints (READ FIRST)

**From `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`:**

❌ **NEVER:**
- Use American medical terminology (acetaminophen, albuterol, epinephrine)
- Reference US sources without Australian context (UpToDate, USMLE)
- Use placeholder content or generic templates
- Skip RAG citations (minimum 3 per scenario, >0.70 confidence per line 26)

✅ **ALWAYS:**
- Use Australian spelling: paracetamol, salbutamol, adrenaline
- Reference Australian sources: eTG, AMH, PBS, AMC Handbook, AHPRA standards
- Include cultural considerations (Aboriginal, CALD patients)
- Validate all medical content with RAG citations

**From `/home/dev/Development/irStudy/constraints/1-medical-accuracy.md`:**
- Australian drug names mandatory (line 31)
- 100% real content, NO templates (line 23)
- RAG citations required: exactly 3 per MCQ/OSCE, >0.70 confidence (line 26)

---

## 📋 Implementation Guide

### Step 1: Read Clinical Review Document (30 min)

```bash
cd /home/dev/Development/irStudy

# Read complete clinical review
cat AI_OSCE_CLINICAL_REVIEW_REPORT.md

# Key sections to extract:
# - Section 1.2: Expanded AMC Rubric (lines 38-200)
# - Section 2: Diverse Scenarios (3 complete examples with RAG citations)
# - Section 3: RAG Validation Specification
# - Section 6: Golden Dataset Specification

# Verify file exists and is readable
[ -f AI_OSCE_CLINICAL_REVIEW_REPORT.md ] && echo "✅ Clinical review found" || echo "❌ File missing"
```

### Step 2: Extract Expanded AMC Rubric (1 hour)

```bash
# Create clinical content directory
mkdir -p planning/phase0-critical-fixes-2026-02-09/clinical-content

# Extract expanded AMC rubric from Clinical Review Section 1.2
# Lines 38-200 contain the complete rubric with all scoring levels
```

**CREATE FILE**: `planning/phase0-critical-fixes-2026-02-09/clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md`

**CONTENT STRUCTURE** (copy from AI_OSCE_CLINICAL_REVIEW_REPORT.md Section 1.2):
```markdown
# AMC 15-Mark OSCE Rubric - Expanded for AI Examiner

## Communication Skills (0-3 marks)

### 3 marks (Excellent)
**Criteria:** Establishes rapport within first 30 seconds; uses open-ended questions consistently...
**Example:** "Student introduced themselves clearly, made appropriate eye contact..."
**RAG Citation:** (AMC Handbook of Clinical Assessment, p.23-25: "Communication Skills Marking Criteria")

### 2 marks (Satisfactory)
[Full criteria from Clinical Review]

### 1 mark (Below Standard)
[Full criteria from Clinical Review]

### 0 marks (Poor/Unsafe)
[Full criteria from Clinical Review]
**Auto-Fail Trigger:** Any unprofessional behavior, breach of confidentiality...

## Clinical Reasoning (0-4 marks)
[Complete section from Clinical Review Section 1.2, lines 61-82]

## Information Gathering (0-4 marks)
[Complete section from Clinical Review Section 1.2, lines 83-105]

## Management (0-2 marks)
[Complete section from Clinical Review Section 1.2, lines 106-124]

## Professionalism (0-2 marks)
[Complete section from Clinical Review Section 1.2, lines 126-139]

## AMC Scoring Thresholds
**PASS:** ≥9/15 (60%) AND no critical errors AND minimum scores:
- Communication: ≥1
- Clinical Reasoning: ≥2
- Information Gathering: ≥2
- Management: ≥1 (if management station)
- Professionalism: ≥1

## Critical Errors (Auto-Fail)
[Complete section from Clinical Review Section 1.2, lines 154-186]

## Common IMG Student Mistakes
[Complete section from Clinical Review Section 1.2, lines 188-200]
```

### Step 3: Extract 3 Diverse Scenarios (2 hours)

**CREATE FILE**: `planning/phase0-critical-fixes-2026-02-09/clinical-content/DIVERSE_CLINICAL_SCENARIOS.md`

**SCENARIOS TO EXTRACT** (from AI_OSCE_CLINICAL_REVIEW_REPORT.md Section 2):

1. **Aboriginal Patient - Community-Acquired Pneumonia**
   - Extract complete scenario (Uncle Billy Williams)
   - Include cultural considerations, RAG citations
   - Source: Clinical Review Section 2.1

2. **CALD Patient - Postnatal Depression**
   - Extract complete scenario (Mei Chen)
   - Include language barriers, cultural stigma, interpreter needs
   - Source: Clinical Review Section 2.2

3. **Obstetric Emergency - First Trimester Bleeding**
   - Extract complete scenario (Sarah Thompson)
   - Include emotional state, NSW Health protocols
   - Source: Clinical Review Section 2.3

**VERIFY EACH SCENARIO HAS:**
- Complete patient demographics
- Opening statement
- Progressive disclosure structure (JSONB format)
- Emotional profile with state transitions
- RAG query hints
- Key differentials
- Critical actions (Australian guidelines with timeframes)
- Cultural considerations

### Step 4: Create RAG Validation Specification (1 hour)

**CREATE FILE**: `planning/phase0-critical-fixes-2026-02-09/clinical-content/RAG_VALIDATION_SPECIFICATION.md`

**CONTENT** (from AI_OSCE_CLINICAL_REVIEW_REPORT.md Section 3):
```markdown
# RAG Validation Specification for Medical Accuracy

## Purpose
Prevent AI Patient from providing medically incorrect or dangerous information.

## Requirements

### 1. Confidence Threshold
- Minimum confidence: >0.65 (per PROJECT_CONSTRAINTS.md line 26)
- Ideal confidence: >0.80 for critical medical information
- Reject chunks with confidence <0.65

### 2. Australian Source Filtering
**APPROVED SOURCES ONLY:**
- eTG (Therapeutic Guidelines)
- AMH (Australian Medicines Handbook)
- PBS (Pharmaceutical Benefits Scheme)
- AMC Clinical Examination Handbook
- Cochrane Reviews (with Australian context)
- RANZCOG, RACGP, RACP guidelines
- NSW Health protocols
- Australian Resuscitation Council

**NEVER USE:**
- UpToDate (US-based)
- USMLE materials
- US-only guidelines (ACOG, AHA without Australian equivalent)

### 3. Hallucination Detection
**VERIFY CRITICAL STATEMENTS:**
- Medication dosing (must match AMH)
- Investigation timeframes (must match Australian guidelines)
- Critical actions (must have eTG/AMH citation)
- Red flags (must have evidence in RAG chunks)

**ALGORITHM:**
```python
def validate_ai_response(response: str, rag_chunks: list) -> tuple[bool, list]:
    # Check 1: Confidence threshold
    valid_chunks = [c for c in rag_chunks if c['score'] > 0.65]

    # Check 2: Australian sources only
    valid_chunks = [c for c in valid_chunks if
        any(source in c['metadata']['source'].lower()
            for source in APPROVED_SOURCES)]

    # Check 3: Minimum 1 citation required
    if len(valid_chunks) < 1:
        return False, []

    # Check 4: Extract citations (max 3)
    citations = [
        f"({c['metadata']['source']}, p.{c['metadata']['page']})"
        for c in valid_chunks[:3]
    ]

    return True, citations
```

### 4. Expert Validation Process
- 200 Golden Dataset scenarios
- Each validated by FRACGP/FACEM/FRANZCOG clinician
- AI vs human examiner scoring: ±2 marks tolerance
- Quarterly recalibration required

## Success Criteria
✅ All AI Patient responses have ≥1 RAG citation with confidence >0.65
✅ 100% Australian sources (no US-only materials)
✅ Critical medical statements verified against RAG chunks
✅ Golden Dataset: AI vs human examiner variance ≤±2 marks
```

### Step 5: Define Golden Dataset Specification (1 hour)

**CREATE FILE**: `planning/phase0-critical-fixes-2026-02-09/clinical-content/GOLDEN_DATASET_SPECIFICATION.md`

**CONTENT** (from AI_OSCE_CLINICAL_REVIEW_REPORT.md Section 6):
```markdown
# Golden Dataset Specification - 200 Expert-Validated OSCE Scenarios

## Purpose
Ensure AI Examiner scoring accuracy matches human AMC examiners.

## Dataset Composition

### By Specialty (25 scenarios × 8 specialties = 200 total)
1. Cardiology: 25 scenarios
2. Respiratory: 25 scenarios
3. Gastroenterology: 25 scenarios
4. Neurology: 25 scenarios
5. Endocrinology: 25 scenarios
6. Psychiatry: 25 scenarios
7. Surgery: 25 scenarios
8. Obstetrics & Gynaecology: 25 scenarios

### By Difficulty
- Foundation: 40% (80 scenarios) - Pass rate target: 75-85%
- Intermediate: 40% (80 scenarios) - Pass rate target: 60-70%
- Advanced: 20% (40 scenarios) - Pass rate target: 40-50%

### By Cultural Diversity
- Aboriginal/Torres Strait Islander patients: 20% (40 scenarios)
- CALD patients (diverse backgrounds): 30% (60 scenarios)
- Mainstream Australian patients: 50% (100 scenarios)

## 7-Step Validation Process

### Step 1: Clinical Expert Creation (2 hours per scenario)
**Who:** FRACGP, FACEM, FRANZCOG, RACP Fellows
**Deliverable:** Complete patient persona with:
- Demographics, chief complaint, opening statement
- Progressive disclosure (JSONB structure)
- Emotional profile with state transitions
- Expected differentials
- Critical actions with timeframes
- RAG query hints

### Step 2: AI Patient Simulation Test (30 min per scenario)
**Who:** Medical student actor (PGY1-3 level)
**Process:**
1. Student takes 8-minute OSCE with AI Patient
2. Full conversation transcript recorded
3. Emotional state transitions logged
4. RAG citations validated (all >0.65 confidence)

### Step 3: AI Examiner Scoring (5 min per scenario)
**Process:**
1. AI Examiner scores transcript using AMC 15-mark rubric
2. Structured output: scores per domain + feedback + critical errors
3. AI response logged for comparison

### Step 4: Human Examiner Scoring (15 min per scenario)
**Who:** 3 independent AMC-trained examiners
**Process:**
1. Each examiner scores same transcript (blinded to AI score)
2. Use official AMC 15-mark rubric
3. Record score breakdown + critical errors

### Step 5: Inter-Rater Reliability Testing
**Acceptance Criteria:**
- AI vs Human Examiner 1: ≤±2 marks variance
- AI vs Human Examiner 2: ≤±2 marks variance
- AI vs Human Examiner 3: ≤±2 marks variance
- Human examiners inter-rater agreement: Cohen's kappa >0.70

### Step 6: Iteration (if variance >±2 marks)
**Process:**
1. Analyze discrepancy: AI too harsh? Too lenient? Missed critical error?
2. Adjust AI Examiner prompt (rubric interpretation)
3. Re-score scenario with updated prompt
4. Repeat until variance ≤±2 marks

### Step 7: Final Approval
**Approval Authority:** Clinical Advisor + Senior AMC Examiner
**Criteria:**
- ✅ AI vs human variance ≤±2 marks (all 3 human examiners)
- ✅ Critical error detection 100% accurate
- ✅ Feedback clinically appropriate
- ✅ Australian medical context correct throughout

## Quarterly Recalibration
- Re-validate 20 random scenarios from Golden Dataset (10%)
- Compare AI scores vs new human examiner panel
- Adjust AI prompts if variance increases
- Document any drift in scoring patterns

## Success Criteria
✅ 200 scenarios validated (25 per specialty × 8)
✅ AI vs human examiner: ≤±2 marks variance (100% of scenarios)
✅ Cultural diversity: 20% Aboriginal, 30% CALD
✅ Difficulty distribution: 40% foundation, 40% intermediate, 20% advanced
✅ Quarterly recalibration process documented
```

### Step 6: Add Australian Healthcare Context (1 hour)

**CREATE FILE**: `planning/phase0-critical-fixes-2026-02-09/clinical-content/AUSTRALIAN_HEALTHCARE_CONTEXT.md`

**CONTENT**:
```markdown
# Australian Healthcare System Context for AI OSCE

## Purpose
Ensure AI Patient and AI Examiner understand Australian-specific healthcare delivery.

## Medicare & PBS

### Medicare Item Numbers (Common Investigations)
- **ECG:** Item 11700 ($20.00 rebate, bulk-billed in most practices)
- **Chest X-ray:** Item 58503 ($37.05 rebate)
- **Full Blood Count:** Item 65070 ($16.90 rebate)
- **Troponin (cardiac marker):** Item 66512 ($16.90 rebate)
- **HbA1c (diabetes monitoring):** Item 66551 ($16.90 rebate)

### PBS Medication Restrictions
- **Biologics (e.g., adalimumab):** Authority prescription required
- **Osteoporosis medications (e.g., denosumab):** Streamlined authority
- **Expensive antibiotics (e.g., linezolid):** Authority required with phone approval

**AI Patient Response Example:**
"Doctor, I've been prescribed that biologic injection for my arthritis, but the pharmacist said I need some special approval form?"
(Tests student knowledge of PBS authority prescriptions)

## Emergency Services

### Triple Zero (000)
- National emergency number (NOT 911)
- Operators ask: "Police, Fire, or Ambulance?"
- Ambulance services vary by state:
  - NSW: Free for pensioners, $401 + $3.62/km for others
  - QLD: Free for QLD residents
  - VIC: $1,234 for emergency callout

**AI Patient Scenario:**
"Should I call an ambulance, doctor? I'm worried about the cost..."
(Tests student knowledge of ambulance cost variation, ability to prioritize patient safety)

## AHPRA Standards

### Mandatory Reporting
- **Sexual misconduct** with patient: MUST report
- **Intoxication** affecting patient care: MUST report
- **Significant departure from accepted standards:** MUST report

**OSCE Scenario Example:**
"My previous doctor made me feel uncomfortable during the examination..."
(Tests student response to mandatory reporting trigger)

## NSW Health Protocols

### RPA Newborn Care eTG Antenatal Guidelines
- **First trimester bleeding:** Refer to Early Pregnancy Assessment Unit (EPAU)
- **Gestational diabetes screening:** OGTT at 24-28 weeks for all women
- **Group B Strep:** Screen at 36 weeks, intrapartum antibiotics if positive

**AI Patient Scenario (ObGyn):**
"I'm 8 weeks pregnant and had some bleeding this morning. The GP said to come to hospital."
(Tests knowledge of EPAU referral pathway, not ER)

## Rural & Remote Healthcare

### RFDS (Royal Flying Doctor Service)
- Aeromedical retrievals for remote areas
- Telehealth consultations
- Primary healthcare clinics

**AI Patient Scenario:**
"I live 300km from the nearest hospital, doctor. If something goes wrong, how quickly can help arrive?"
(Tests rural healthcare knowledge, RFDS awareness)

## Cultural Considerations

### Aboriginal & Torres Strait Islander Health
- **"Sorry Business":** Extended family mourning period (can affect appointments)
- **Shame:** Concept affecting disclosure of sensitive topics
- **Family decision-making:** Involve extended family, not just patient
- **Traditional healing:** Respect for bush medicine alongside Western medicine

**Communication Example:**
"Uncle Billy, I understand this is difficult to talk about. Would you like your daughter here while we discuss your treatment options?"

### CALD (Culturally and Linguistically Diverse)
- **TIS (Translating and Interpreting Service):** 24/7 phone interpretation
  - Number: 131 450
  - Free for medical appointments
- **Family member interpreters:** Generally avoid (privacy, accuracy concerns)
- **Written consent:** Requires professional interpreter

**AI Patient Scenario:**
"My English not so good, doctor. Can my daughter translate?"
(Tests student knowledge of TIS, professional interpreter requirements)

## Medical Terminology (Australian vs US)

| Australian | US Equivalent | Context |
|-----------|---------------|---------|
| Paracetamol | Acetaminophen | Analgesia |
| Salbutamol | Albuterol | Asthma |
| Adrenaline | Epinephrine | Anaphylaxis |
| GP | Family doctor | Primary care |
| 000 | 911 | Emergency services |
| Casualty/ED | ER | Emergency department |
| Theatre | OR | Operating room |
| Registrar | Resident (US PGY4+) | Training doctor |
| Consultant | Attending | Qualified specialist |

## Units of Measurement

**Blood Glucose:**
- Australian: mmol/L
- US: mg/dL
- Normal fasting: 3.5-5.5 mmol/L (63-99 mg/dL)

**AI Examiner:** Must mark student WRONG if they use mg/dL without conversion

**Cholesterol:**
- Total cholesterol: <5.5 mmol/L
- LDL: <2.0 mmol/L
- HDL: >1.0 mmol/L (men), >1.3 mmol/L (women)

## Success Criteria
✅ All AI Patient scenarios use Australian terminology (paracetamol, GP, 000)
✅ Medicare item numbers included where relevant
✅ PBS restrictions mentioned for expensive medications
✅ AHPRA standards referenced (mandatory reporting, informed consent)
✅ NSW Health protocols for obstetrics, emergency management
✅ Cultural considerations for Aboriginal, CALD patients
✅ Units in mmol/L (NOT mg/dL)
```

### Step 7: Prepare Clinical Advisor Review Package (30 min)

```bash
# Create Clinical Advisor review package
mkdir -p planning/phase0-critical-fixes-2026-02-09/clinical-advisor-review

# Create summary document for Clinical Advisor
cat > planning/phase0-critical-fixes-2026-02-09/clinical-advisor-review/CLINICAL_ADVISOR_REVIEW_PACKAGE.md << 'EOF'
# Clinical Advisor Review Package - Phase 0 Week 0.1

## Purpose
Obtain Clinical Advisor approval for all clinical content before Phase 1 implementation.

## Documents for Review

### 1. Expanded AMC 15-Mark Rubric
**File:** `clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md`
**Review Time:** 2-3 hours
**Questions for Clinical Advisor:**
- Are scoring criteria aligned with official AMC standards?
- Are examples of "Excellent" vs "Satisfactory" vs "Poor" realistic?
- Are critical errors (auto-fail) comprehensive?
- Are common IMG mistakes accurate?
- **Approval Required:** YES/NO with written sign-off

### 2. Diverse Clinical Scenarios (3 scenarios)
**File:** `clinical-content/DIVERSE_CLINICAL_SCENARIOS.md`
**Review Time:** 1-2 hours
**Questions for Clinical Advisor:**
- Are clinical presentations medically accurate?
- Are progressive disclosure sequences realistic?
- Are emotional states appropriate for each scenario?
- Are critical actions aligned with Australian guidelines (eTG, NSW Health)?
- Are cultural considerations authentic (Aboriginal, CALD)?
- **Approval Required:** YES/NO for each scenario

### 3. RAG Validation Specification
**File:** `clinical-content/RAG_VALIDATION_SPECIFICATION.md`
**Review Time:** 30 min
**Questions for Clinical Advisor:**
- Is confidence threshold (>0.65) appropriate?
- Are approved Australian sources comprehensive?
- Is hallucination detection mechanism adequate?
- **Approval Required:** YES/NO

### 4. Golden Dataset Specification
**File:** `clinical-content/GOLDEN_DATASET_SPECIFICATION.md`
**Review Time:** 1 hour
**Questions for Clinical Advisor:**
- Is 7-step validation process feasible?
- Is ±2 marks variance acceptable for AI vs human examiner?
- Is sample size (200 scenarios) sufficient?
- Can you recommend FRACGP/FACEM fellows for validation panel?
- **Approval Required:** YES/NO

### 5. Australian Healthcare Context
**File:** `clinical-content/AUSTRALIAN_HEALTHCARE_CONTEXT.md`
**Review Time:** 30 min
**Questions for Clinical Advisor:**
- Are Medicare item numbers correct?
- Are PBS restrictions accurately described?
- Are AHPRA mandatory reporting triggers correct?
- Are cultural considerations appropriate?
- **Approval Required:** YES/NO

## Approval Process

**Deadline:** 5 business days from delivery
**Format:** Email approval or written sign-off document
**Contact:** [Clinical Advisor Name/Email to be inserted]

**Required Statement:**
"I, [Name], [Credentials], approve the clinical content prepared for the AI OSCE Simulation system Phase 0 Week 0.1. I confirm that all medical information is accurate, aligned with AMC standards, and appropriate for Australian medical practice."

**Signature:** ________________
**Date:** ________________

## Next Steps After Approval

1. ✅ Clinical Advisor approves → Proceed to Phase 0 Week 0.2 (Security Hardening)
2. ❌ Clinical Advisor requests changes → Iterate on specific sections, re-submit

## Timeline

- **Day 1-2:** Prepare all documents (this task)
- **Day 3:** Submit to Clinical Advisor
- **Day 3-7:** Clinical Advisor review (5 business days)
- **Day 8:** Approval received OR iteration begins
- **Day 9:** Proceed to Phase 0 Week 0.2

**Critical Path:** Clinical Advisor approval blocks Phase 0 Week 0.2 and ALL of Phase 1
EOF

echo "✅ Clinical Advisor review package created"
```

---

## ✅ Validation Checklist

**Before marking this task complete, verify:**

```bash
# Check 1: All files created
files=(
    "planning/phase0-critical-fixes-2026-02-09/clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md"
    "planning/phase0-critical-fixes-2026-02-09/clinical-content/DIVERSE_CLINICAL_SCENARIOS.md"
    "planning/phase0-critical-fixes-2026-02-09/clinical-content/RAG_VALIDATION_SPECIFICATION.md"
    "planning/phase0-critical-fixes-2026-02-09/clinical-content/GOLDEN_DATASET_SPECIFICATION.md"
    "planning/phase0-critical-fixes-2026-02-09/clinical-content/AUSTRALIAN_HEALTHCARE_CONTEXT.md"
    "planning/phase0-critical-fixes-2026-02-09/clinical-advisor-review/CLINICAL_ADVISOR_REVIEW_PACKAGE.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file MISSING"
    fi
done

# Check 2: AMC Rubric has all 5 domains
grep -q "Communication Skills (0-3 marks)" planning/phase0-critical-fixes-2026-02-09/clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md && echo "✅ Communication domain present" || echo "❌ Missing"
grep -q "Clinical Reasoning (0-4 marks)" planning/phase0-critical-fixes-2026-02-09/clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md && echo "✅ Clinical Reasoning domain present" || echo "❌ Missing"
grep -q "Information Gathering (0-4 marks)" planning/phase0-critical-fixes-2026-02-09/clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md && echo "✅ Information Gathering domain present" || echo "❌ Missing"
grep -q "Management (0-2 marks)" planning/phase0-critical-fixes-2026-02-09/clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md && echo "✅ Management domain present" || echo "❌ Missing"
grep -q "Professionalism (0-2 marks)" planning/phase0-critical-fixes-2026-02-09/clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md && echo "✅ Professionalism domain present" || echo "❌ Missing"

# Check 3: Scenarios have RAG citations
grep -q "RAG Citation" planning/phase0-critical-fixes-2026-02-09/clinical-content/DIVERSE_CLINICAL_SCENARIOS.md && echo "✅ RAG citations present" || echo "❌ No RAG citations"

# Check 4: Australian terminology used (NOT American)
if grep -q "acetaminophen\|albuterol\|epinephrine\|911\|ER\|OR" planning/phase0-critical-fixes-2026-02-09/clinical-content/*.md; then
    echo "❌ FAIL: American terminology detected"
else
    echo "✅ PASS: Australian terminology only"
fi

# Check 5: Confidence threshold specified
grep -q ">0.65" planning/phase0-critical-fixes-2026-02-09/clinical-content/RAG_VALIDATION_SPECIFICATION.md && echo "✅ Confidence threshold >0.65" || echo "❌ Threshold missing"
```

---

## 🎯 Success Criteria

**This task is DONE when ALL of these are true:**

1. ✅ AMC_15_MARK_RUBRIC_EXPANDED.md created with:
   - All 5 domains (Communication, Clinical Reasoning, Information Gathering, Management, Professionalism)
   - Detailed criteria for each mark level (3, 2, 1, 0 for Communication; 4, 3, 2, 1, 0 for others)
   - Examples for each level
   - RAG citations (AMC Handbook, Talley & O'Connor)
   - Critical errors (auto-fail list)
   - Common IMG mistakes

2. ✅ DIVERSE_CLINICAL_SCENARIOS.md created with 3 complete scenarios:
   - Aboriginal patient (pneumonia, cultural considerations)
   - CALD patient (postnatal depression, interpreter needs)
   - Obstetric emergency (first trimester bleeding)
   - Each with: demographics, opening statement, progressive disclosure, emotional profile, RAG citations, critical actions

3. ✅ RAG_VALIDATION_SPECIFICATION.md created with:
   - Confidence threshold: >0.65 (per PROJECT_CONSTRAINTS.md line 26)
   - Australian sources only (eTG, AMH, PBS, AMC Handbook)
   - Hallucination detection algorithm
   - Expert validation process

4. ✅ GOLDEN_DATASET_SPECIFICATION.md created with:
   - 200 scenarios (25 per specialty × 8)
   - 7-step validation process
   - AI vs human examiner: ±2 marks tolerance
   - Quarterly recalibration plan

5. ✅ AUSTRALIAN_HEALTHCARE_CONTEXT.md created with:
   - Medicare item numbers
   - PBS restrictions
   - AHPRA standards (mandatory reporting)
   - NSW Health protocols
   - Cultural considerations (Aboriginal, CALD)
   - Australian terminology table

6. ✅ CLINICAL_ADVISOR_REVIEW_PACKAGE.md created with:
   - Summary of all documents for review
   - Approval process defined
   - Timeline specified

7. ✅ NO American terminology (acetaminophen, albuterol, 911, ER) - all Australian

8. ✅ All files in `planning/phase0-critical-fixes-2026-02-09/clinical-content/` directory

---

## 🔄 When Complete

```bash
# 1. Verify all files created
ls -lh planning/phase0-critical-fixes-2026-02-09/clinical-content/
ls -lh planning/phase0-critical-fixes-2026-02-09/clinical-advisor-review/

# 2. Create summary
cat > planning/phase0-critical-fixes-2026-02-09/PHASE0_WEEK01_SUMMARY.md << 'EOF'
# Phase 0 Week 0.1 Complete - Clinical Accuracy Materials Ready

## Deliverables Created

1. ✅ AMC_15_MARK_RUBRIC_EXPANDED.md (5 domains, 3-4 levels each, with examples)
2. ✅ DIVERSE_CLINICAL_SCENARIOS.md (3 scenarios with RAG citations)
3. ✅ RAG_VALIDATION_SPECIFICATION.md (confidence >0.65, Australian sources)
4. ✅ GOLDEN_DATASET_SPECIFICATION.md (200 scenarios, 7-step validation)
5. ✅ AUSTRALIAN_HEALTHCARE_CONTEXT.md (Medicare, PBS, AHPRA, cultural)
6. ✅ CLINICAL_ADVISOR_REVIEW_PACKAGE.md (approval process)

## Next Steps

1. Submit to Clinical Advisor for review (5 business day SLA)
2. Await approval (BLOCKING for Phase 0 Week 0.2)
3. If approved → Proceed to PRD_PHASE0_WEEK02_SECURITY_HARDENING.md
4. If changes requested → Iterate and re-submit

## Timeline

- Day 1-2: Materials prepared (COMPLETE)
- Day 3: Submit to Clinical Advisor
- Day 3-7: Clinical Advisor review
- Day 8: Approval OR iteration
- Day 9: Proceed to Week 0.2
EOF

# 3. Git commit (DO NOT run until all files confirmed created)
echo "✅ Phase 0 Week 0.1 materials ready for Clinical Advisor review"
echo "Next: Submit to Clinical Advisor, await approval before Week 0.2"
```

---

**COMPLETION COMMAND** (run ONLY after all validation checks pass):

```bash
echo "====================================="
echo "✅ PHASE0_WEEK01 COMPLETE"
echo "====================================="
echo ""
echo "Deliverables:"
echo "- AMC 15-Mark Rubric (Expanded)"
echo "- 3 Diverse Clinical Scenarios"
echo "- RAG Validation Specification"
echo "- Golden Dataset Specification (200 scenarios)"
echo "- Australian Healthcare Context"
echo "- Clinical Advisor Review Package"
echo ""
echo "Next Steps:"
echo "1. Submit to Clinical Advisor"
echo "2. Await approval (5 business days)"
echo "3. If approved → Start PRD_PHASE0_WEEK02_SECURITY_HARDENING.md"
echo ""
echo "BLOCKING: Phase 0 Week 0.2 cannot start without Clinical Advisor approval"
echo "====================================="
```

---

**END OF PRD** - AUTONOMOUS EXECUTION MODE - NO QUESTIONS
