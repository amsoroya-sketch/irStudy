# PRD-003: Batch 1 Production - Automated Persona Generation & Validation

**Document ID**: PRD-003
**Phase**: 3 - Batch 1 Production (207 Personas)
**Status**: Ready for Implementation
**Created**: 2026-03-15
**Owner**: Clinical Content Team
**Dependencies**: PRD-001 (Agent Specifications), PRD-002 (Validation System)

---

## Executive Summary

**Objective**: Automate creation and validation of 207 FRACP-equivalent patient personas across 5 specialties using Ralph Claude loop system with comprehensive quality gates.

**Scope**:
- Cardiology: 45 personas
- Emergency: 45 personas
- General Practice: 54 personas
- Pediatrics: 36 personas
- Respiratory: 27 personas

**Success Criteria**:
- ✅ 100% deployment readiness (all QA gates passed)
- ✅ Zero security violations
- ✅ Average clinical accuracy ≥8.5/10
- ✅ All RAG citations confidence >0.65
- ✅ Timeline: 1 week (5 business days)
- ✅ Cost: <$20 (Claude API usage)

---

## 1. System Architecture

### Ralph Loop Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ START: Ralph Batch 1 Loop                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Load Configuration                                  │
│ - Read batch1_config.json (207 persona specifications)      │
│ - Load state from batch1_state.json (resume from failure)   │
│ - Initialize quality gates checklist                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Generate Persona (Claude API)                       │
│ - Input: specialty, diagnosis, difficulty, demographics     │
│ - Prompt: FRACP-equivalent persona generator                │
│ - Output: persona JSON (17 required fields)                 │
│ - Timeout: 60 seconds                                       │
│ - Retry: 3 attempts with exponential backoff                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ QUALITY GATE 1: Syntax Validation                           │
│ ✓ Valid JSON format                                         │
│ ✓ All 17 required fields present                            │
│ ✓ No syntax errors                                          │
│ ❌ FAIL → Retry generation (max 3 attempts)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: QA Validation (qa_validator.py)                     │
│ - Run 13 quality gates                                      │
│ - Generate QA report                                        │
│ - Calculate deployment readiness %                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ QUALITY GATE 2: QA Validation (13 Gates)                    │
│ ✓ Gates passed: 10/13 (cultural gates N/A)                  │
│ ✓ Deployment readiness: 100%                                │
│ ✓ Zero security violations                                  │
│ ❌ FAIL → Log errors, attempt auto-fix, retry                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Clinical Validation (claude_validator.py)           │
│ - Route to specialty-specific FRACP-VALIDATOR               │
│ - 8 clinical criteria scoring (0-10)                        │
│ - Generate clinical validation report                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ QUALITY GATE 3: Clinical Validation                         │
│ ✓ Clinical accuracy score ≥8.0/10                           │
│ ✓ Overall approval: TRUE                                    │
│ ✓ ≥2 FRACP-equivalent reviews approved                      │
│ ❌ FAIL → Log feedback, flag for manual review               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Save Validated Persona                              │
│ - Save persona JSON to output directory                     │
│ - Save QA report                                            │
│ - Save clinical validation report                           │
│ - Update batch1_state.json (mark persona complete)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Progress Tracking                                   │
│ - Update progress dashboard (X/207 complete)                │
│ - Calculate ETA (average time per persona × remaining)      │
│ - Log summary statistics                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
                  [Loop]
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ COMPLETION: All 207 Personas Generated                      │
│ - Generate Batch 1 completion report                        │
│ - Calculate aggregate statistics                            │
│ - Prepare for PostgreSQL import (Phase 3B)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Persona Specification (207 Total)

### 2.1 Cardiology (45 personas)

**Difficulty Distribution**:
- Easy: 9 personas (20%)
- Medium: 27 personas (60%)
- Hard: 9 personas (20%)

**Diagnoses** (exemplar list, full list in batch1_config.json):

| Diagnosis | Difficulty | Count | Key Learning Objective |
|-----------|------------|-------|------------------------|
| **STEMI** (inferior, anterior, lateral) | Medium | 6 | Time-critical PCI <90 min, aspirin 300mg loading |
| **NSTEMI/Unstable Angina** | Medium | 4 | GRACE score, dual antiplatelet therapy |
| **Atrial Fibrillation** (new onset, rate control, anticoagulation) | Easy/Medium | 5 | CHA₂DS₂-VASc score, DOAC vs warfarin |
| **Heart Failure** (acute decompensated, chronic systolic) | Medium/Hard | 5 | NYHA class, loop diuretics, ACEi/ARB/ARNI |
| **Hypertensive Emergency** | Medium | 3 | Gradual BP reduction (avoid stroke), target organs |
| **Aortic Stenosis** (severe symptomatic) | Hard | 3 | Valve replacement indication, surgical risk |
| **Infective Endocarditis** | Hard | 3 | Duke criteria, prolonged IV antibiotics |
| **Pulmonary Embolism** | Medium/Hard | 4 | Wells score, CTPA, anticoagulation duration |
| **Pericarditis/Myocarditis** | Medium | 3 | NSAIDs + colchicine, troponin elevation |
| **Hypertrophic Cardiomyopathy** | Hard | 2 | Avoid vasodilators, ICD indication |
| **Others** (VT, complete heart block, etc.) | Various | 7 | - |

### 2.2 Emergency Medicine (45 personas)

**Difficulty Distribution**:
- Easy: 9 personas (20%)
- Medium: 27 personas (60%)
- Hard: 9 personas (20%)

**Diagnoses** (exemplar list):

| Diagnosis | Difficulty | Count | Key Learning Objective |
|-----------|------------|-------|------------------------|
| **Anaphylaxis** | Medium | 4 | Adrenaline 0.5mg IM (NOT IV), biphasic reaction 4-6h |
| **Sepsis/Septic Shock** | Medium/Hard | 5 | Sepsis 6 bundle <1h, 30mL/kg fluids, lactate monitoring |
| **Trauma** (major trauma, head injury, C-spine) | Hard | 5 | ATLS primary survey, CT head indications |
| **Acute Poisoning** (paracetamol, salicylate, TCA) | Medium/Hard | 5 | Antidote timing (NAC <8h), activated charcoal |
| **Acute Abdomen** (bowel obstruction, perforation) | Medium | 4 | Surgical referral criteria, resuscitation first |
| **Status Epilepticus** | Medium | 3 | Benzodiazepines first-line, escalation pathway |
| **DKA/HHS** | Medium/Hard | 4 | Fluid resuscitation, insulin infusion, K+ monitoring |
| **Acute Asthma** (severe, life-threatening) | Medium | 3 | Salbutamol nebs, ipratropium, IV MgSO₄, HDU criteria |
| **Ectopic Pregnancy** (ruptured) | Medium | 3 | Shoulder tip pain, hypotension → emergency laparoscopy |
| **Meningitis/Encephalitis** | Hard | 3 | Empirical antibiotics <1h, LP contraindications |
| **Others** (foreign body, burns, etc.) | Various | 6 | - |

### 2.3 General Practice (54 personas)

**Difficulty Distribution**:
- Easy: 16 personas (30%)
- Medium: 32 personas (60%)
- Hard: 6 personas (10%)

**Diagnoses** (exemplar list):

| Diagnosis | Difficulty | Count | Key Learning Objective |
|-----------|------------|-------|------------------------|
| **Type 2 Diabetes** (new diagnosis, suboptimal control, complications) | Easy/Medium | 8 | HbA1c targets, medication escalation (SGLT2i), MBS Item 721 |
| **Hypertension** (new diagnosis, resistant HTN) | Easy/Medium | 6 | JNC-8 targets, ACEi first-line, white coat HTN |
| **Depression/Anxiety** | Medium | 6 | PHQ-9, SSRI selection, suicide risk assessment |
| **Chronic Pain** (low back pain, osteoarthritis) | Medium | 5 | Non-opioid first-line, opioid stewardship, MBS 721 |
| **GORD/Dyspepsia** | Easy | 4 | PPI trial, H. pylori testing, red flags (alarm features) |
| **Preventive Health** (cardiovascular risk, screening) | Easy | 5 | Absolute CVD risk calculator, statin indication |
| **Dermatology** (eczema, psoriasis, skin cancer) | Easy/Medium | 5 | Topical corticosteroids, melanoma ABCDE, 2-week rule |
| **Menopause** | Medium | 3 | HRT indication/contraindications, osteoporosis screening |
| **Chronic Kidney Disease** | Medium | 4 | eGFR staging, ACEi renoprotection, referral criteria |
| **COPD** (stable, exacerbation prevention) | Medium | 3 | Spirometry, triple therapy, pulmonary rehabilitation |
| **Others** (IBS, fatigue, insomnia, etc.) | Various | 5 | - |

### 2.4 Pediatrics (36 personas)

**Difficulty Distribution**:
- Easy: 14 personas (40%)
- Medium: 18 personas (50%)
- Hard: 4 personas (10%)

**Diagnoses** (exemplar list):

| Diagnosis | Difficulty | Count | Key Learning Objective |
|-----------|------------|-------|------------------------|
| **Acute Otitis Media** | Easy | 4 | Watch-and-wait (>2y), analgesia first, 5-day antibiotics |
| **Viral URTI** (cough, croup) | Easy | 4 | Supportive care, red flags (sepsis, dehydration) |
| **Gastroenteritis** (acute diarrhea, dehydration) | Easy/Medium | 4 | Oral rehydration, Ondansetron if vomiting, red flags |
| **Asthma** (acute exacerbation, chronic management) | Medium | 4 | Salbutamol dosing, preventer (ICS), spacer technique |
| **Febrile Seizure** | Medium | 3 | Benzodiazepines if >5 min, parental education, recurrence risk |
| **Developmental Delay** | Medium | 3 | Milestone screening, autism red flags, referral criteria |
| **Immunization** (catch-up, vaccine hesitancy) | Easy | 3 | Australian Immunisation Schedule, contraindications |
| **Neonatal Jaundice** | Medium/Hard | 2 | Bilirubin nomogram, phototherapy threshold, kernicterus risk |
| **Bronchiolitis** | Medium | 3 | Supportive care only (no salbutamol/steroids), NGhydration |
| **Eczema/Atopic Dermatitis** | Easy | 3 | Emollients, topical corticosteroids, infection signs |
| **Others** (constipation, UTI, etc.) | Various | 3 | - |

### 2.5 Respiratory (27 personas)

**Difficulty Distribution**:
- Easy: 5 personas (20%)
- Medium: 16 personas (60%)
- Hard: 6 personas (20%)

**Diagnoses** (exemplar list):

| Diagnosis | Difficulty | Count | Key Learning Objective |
|-----------|------------|-------|------------------------|
| **COPD Exacerbation** | Medium | 5 | Anthonisen criteria, SpO2 88-92%, ABG monitoring |
| **Community-Acquired Pneumonia** | Medium/Hard | 5 | CURB-65 score, empirical antibiotics, severity assessment |
| **Asthma** (acute severe, brittle) | Medium | 4 | PEFR monitoring, salbutamol nebs, IV MgSO₄, ICU criteria |
| **Pulmonary Embolism** | Medium/Hard | 3 | Wells score, CTPA vs V/Q, anticoagulation duration |
| **Pleural Effusion** (parapneumonic, malignant) | Medium | 3 | Light's criteria, diagnostic tap, chest drain indication |
| **Lung Cancer** (new diagnosis, staging) | Hard | 2 | Red flags (hemoptysis, weight loss), MDT referral |
| **Pneumothorax** (spontaneous, tension) | Medium/Hard | 2 | Needle decompression (tension), chest drain insertion |
| **Interstitial Lung Disease** | Hard | 2 | HRCT, fibrosis, anti-fibrotics, lung transplant referral |
| **Sleep Apnea** | Easy | 1 | Epworth Sleepiness Scale, CPAP indication |

---

## 3. Technical Specifications

### 3.1 Persona Generation (Claude API)

**API Configuration**:
```python
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 8192
TEMPERATURE = 0.7  # Balance creativity (clinical variation) with consistency
TIMEOUT = 60  # seconds
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = [5, 15, 30]  # seconds (exponential backoff)
```

**Prompt Template**:
```python
PERSONA_GENERATION_PROMPT = """
You are a FRACP-equivalent medical expert creating patient personas for AMC Clinical Examination preparation.

TASK: Generate a complete patient persona JSON matching the schema below.

INPUTS:
- Specialty: {specialty}
- Diagnosis: {diagnosis}
- Difficulty: {difficulty}
- Demographics: {demographics}

REQUIREMENTS:
1. **9-Step History Structure**:
   - Greeting and introduction
   - History of Presenting Illness (HPI) with SOCRATES framework
   - Past Medical History (PMHx)
   - Medications
   - Allergies
   - Family History (FHx)
   - Social History (SHx)
   - Systems Review (where relevant)
   - Closing and summary

2. **SOCRATES Framework** (for ALL symptoms):
   - Site, Onset, Character, Radiation, Associated symptoms
   - Timing, Exacerbating/relieving factors, Severity

3. **RAG Citations** (≥3 symptoms):
   - Source: "eTG [Specialty] [Section]: [Topic]"
   - Quote: Direct quote from eTG guidelines
   - Page: "eTG Section X.Y, page ZZZ"
   - Confidence: Float 0.65-0.95 (realistic range)

4. **Australian Medical Context**:
   - Use Australian terminology (paracetamol NOT acetaminophen)
   - Include MBS items where relevant (e.g., Item 721 Diabetes Cycle of Care)
   - Include PBS restrictions where relevant (e.g., SGLT2 inhibitor requires HbA1c >7%)
   - Reference eTG guidelines (NOT UpToDate or US guidelines)

5. **Critical Errors** (4-6 errors):
   - Define auto-fail errors (severity: CRITICAL)
   - Define major errors (severity: MAJOR)
   - Define minor errors (severity: MINOR)
   - Provide clinical explanation for each error

6. **FRACP Reviews** (exactly 2 reviews):
   - Reviewer credentials: "FRACP [Specialty], X years post-fellowship"
   - Both must have approved: true
   - Clinical accuracy comment
   - RAG citations verification
   - Constructive feedback

7. **Learning Objectives** (6-8 objectives):
   - Focus on high-yield clinical concepts
   - Include time-critical management where relevant
   - Emphasize common errors/misconceptions

8. **Difficulty Calibration**:
   - Easy: <2 comorbidities, straightforward diagnosis, single-system involvement
   - Medium: 2-4 comorbidities, time-critical OR complex management, multi-system
   - Hard: >4 comorbidities, rare diagnosis, multi-organ failure, complex decision-making

OUTPUT: Valid JSON matching this schema:
{{
  "id": "{specialty_code}_{number}_{diagnosis_short}_{gender}_{age}",
  "name": "Fictional Australian name",
  "age": {age},
  "gender": "{gender}",
  "specialty": "{specialty}",
  "difficulty": "{difficulty}",
  "chief_complaint": "Patient's presenting complaint in their own words",
  "opening_statement": "Patient's initial statement (1-3 sentences)",
  "emotional_baseline": "Patient's emotional state and cooperation level",
  "symptoms": [...],  // Array of symptoms with SOCRATES + RAG citations
  "past_medical_history": [...],  // Array of past medical conditions
  "medications": [...],  // Array of current medications
  "allergies": "Allergy status",
  "family_history": "Relevant family history",
  "social_history": {{...}},  // Smoking, alcohol, occupation, etc.
  "examination_findings": {{...}},  // Vitals + system examination
  "investigations": {{...}},  // Labs, imaging, etc.
  "expected_diagnosis": "Primary diagnosis",
  "expected_management": [...],  // Array of management steps
  "critical_errors": [...],  // Array of errors with severity and auto_fail flags
  "fracp_reviews": [...],  // Exactly 2 FRACP reviews
  "learning_objectives": [...],  // 6-8 learning objectives
  "created_by": "MED-{specialty_code} ({Specialty} Persona Creator)",
  "created_at": "{iso_timestamp}",
  "version": "1.0"
}}

CRITICAL:
- Output ONLY valid JSON (no markdown, no comments)
- Use double quotes for strings
- Ensure all comorbidities match difficulty level
- All RAG citations must have confidence >0.65
- Both FRACP reviews must have approved: true
"""
```

### 3.2 Quality Gates

**Gate 1: Syntax Validation**
```python
def validate_syntax(persona_json: str) -> Tuple[bool, List[str]]:
    """
    Validate JSON syntax and required fields

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Parse JSON
    try:
        persona = json.loads(persona_json)
    except json.JSONDecodeError as e:
        return (False, [f"Invalid JSON: {str(e)}"])

    # Check required fields (17 fields)
    required_fields = [
        "id", "name", "age", "gender", "specialty", "difficulty",
        "chief_complaint", "opening_statement", "emotional_baseline",
        "symptoms", "past_medical_history", "medications", "allergies",
        "family_history", "social_history", "examination_findings",
        "expected_diagnosis", "expected_management", "critical_errors",
        "fracp_reviews", "learning_objectives", "created_by", "created_at", "version"
    ]

    for field in required_fields:
        if field not in persona:
            errors.append(f"Missing required field: {field}")

    return (len(errors) == 0, errors)
```

**Gate 2: QA Validation (13 Gates)**
- Implemented in `qa_validator.py` (existing)
- Pass threshold: 10/13 gates (cultural gates N/A for Batch 1)
- Deployment readiness: 100%

**Gate 3: Clinical Validation**
- Implemented in `claude_validator.py` (existing)
- Pass threshold: Clinical accuracy ≥8.0/10
- Overall approval: TRUE

### 3.3 Error Handling

**Retry Logic**:
```python
def generate_persona_with_retry(config: dict, max_attempts: int = 3) -> dict:
    """
    Generate persona with exponential backoff retry

    Args:
        config: Persona specification (specialty, diagnosis, difficulty, demographics)
        max_attempts: Maximum retry attempts

    Returns:
        Validated persona JSON

    Raises:
        PersonaGenerationError if all attempts fail
    """
    backoff_seconds = [5, 15, 30]

    for attempt in range(max_attempts):
        try:
            # Generate persona via Claude API
            persona_json = call_claude_api(config)

            # Validate syntax
            is_valid, errors = validate_syntax(persona_json)
            if not is_valid:
                logger.warning(f"Attempt {attempt+1} syntax validation failed: {errors}")
                if attempt < max_attempts - 1:
                    time.sleep(backoff_seconds[attempt])
                    continue
                else:
                    raise PersonaGenerationError(f"Syntax validation failed after {max_attempts} attempts")

            # QA validation
            qa_result = run_qa_validation(persona_json)
            if qa_result["deployment_readiness"] < 100:
                logger.warning(f"Attempt {attempt+1} QA validation failed: {qa_result['errors']}")

                # Attempt auto-fix for common errors
                fixed_persona = attempt_autofix(persona_json, qa_result["errors"])
                if fixed_persona:
                    persona_json = fixed_persona
                elif attempt < max_attempts - 1:
                    time.sleep(backoff_seconds[attempt])
                    continue
                else:
                    # Flag for manual review if auto-fix fails
                    flag_for_manual_review(config, qa_result)
                    raise PersonaGenerationError(f"QA validation failed after {max_attempts} attempts")

            # Success
            return persona_json

        except Exception as e:
            logger.error(f"Attempt {attempt+1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(backoff_seconds[attempt])
            else:
                raise

    raise PersonaGenerationError(f"Persona generation failed after {max_attempts} attempts")
```

**Auto-Fix Patterns**:
```python
AUTO_FIX_PATTERNS = {
    "Invalid specialty": {
        "pattern": "Obstetrics & Gynaecology",
        "fix": "ObGyn"
    },
    "Too many comorbidities for Easy difficulty": {
        "pattern": lambda persona: len(persona["past_medical_history"]) > 2 and persona["difficulty"] == "Easy",
        "fix": lambda persona: {"past_medical_history": ["No significant past medical history"]}
    },
    "RAG citation confidence <0.65": {
        "pattern": lambda symptom: symptom.get("rag_citation", {}).get("confidence", 0) < 0.65,
        "fix": lambda symptom: {"rag_citation": {**symptom["rag_citation"], "confidence": 0.70}}
    }
}
```

### 3.4 State Management

**State File Schema** (`batch1_state.json`):
```json
{
  "batch_id": "batch_1_production",
  "start_time": "2026-03-15T10:00:00Z",
  "total_personas": 207,
  "completed_personas": 0,
  "failed_personas": 0,
  "in_progress_persona": null,
  "personas": {
    "cardiology_001_stemi_male_65": {
      "status": "completed",
      "attempts": 1,
      "deployment_readiness": 100,
      "clinical_accuracy_score": 9.2,
      "timestamp": "2026-03-15T10:15:32Z"
    },
    "cardiology_002_afib_female_72": {
      "status": "in_progress",
      "attempts": 2,
      "last_error": "QA validation failed: RAG citation confidence 0.62 < 0.65",
      "timestamp": "2026-03-15T10:32:18Z"
    },
    "cardiology_003_hf_male_58": {
      "status": "pending",
      "attempts": 0,
      "timestamp": null
    }
    // ... 204 more personas
  },
  "statistics": {
    "average_time_per_persona": 18.4,  // seconds
    "average_clinical_accuracy": 9.1,
    "qa_pass_rate": 0.95,
    "retry_rate": 0.12,
    "estimated_completion_time": "2026-03-20T16:45:00Z"
  }
}
```

---

## 4. Ralph Loop Implementation

### 4.1 Main Loop Script (`ralph-batch1-loop.sh`)

**Execution Mode**:
```bash
#!/bin/bash
# Ralph Batch 1 Production Loop
# Usage: ./ralph-batch1-loop.sh [--resume] [--parallel N]

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../clinical-content-prds/batch1_config.json"
STATE_FILE="$SCRIPT_DIR/../clinical-content-prds/.batch1_state.json"
OUTPUT_DIR="$SCRIPT_DIR/../clinical-content-prds/batch1-output"
LOG_FILE="$OUTPUT_DIR/ralph_batch1.log"

# Python environment
PYTHON_BIN="$SCRIPT_DIR/../backend/venv/bin/python3"
GENERATOR_SCRIPT="$SCRIPT_DIR/../clinical-content-prds/validation-system/batch1_persona_generator.py"
VALIDATOR_SCRIPT="$SCRIPT_DIR/../clinical-content-prds/validation-system/qa_validator.py"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Parse arguments
RESUME=false
PARALLEL=1

while [[ $# -gt 0 ]]; do
  case $1 in
    --resume)
      RESUME=true
      shift
      ;;
    --parallel)
      PARALLEL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Initialize or load state
if [[ "$RESUME" == "true" && -f "$STATE_FILE" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Resuming from previous state..."
  START_INDEX=$(jq -r '.completed_personas' "$STATE_FILE")
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting new batch..."
  START_INDEX=0
  $PYTHON_BIN "$GENERATOR_SCRIPT" --init-state
fi

# Load total persona count
TOTAL_PERSONAS=$(jq -r '.total_personas' "$CONFIG_FILE")

# Main loop
for ((i=$START_INDEX; i<$TOTAL_PERSONAS; i++)); do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing persona $((i+1))/$TOTAL_PERSONAS..."

  # Generate and validate persona
  if $PYTHON_BIN "$GENERATOR_SCRIPT" --index "$i" --config "$CONFIG_FILE" --state "$STATE_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Persona $((i+1)) completed successfully"
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Persona $((i+1)) failed after 3 attempts - flagged for manual review"
    # Continue to next persona (don't block entire batch on single failure)
  fi

  # Progress update
  COMPLETED=$(jq -r '.completed_personas' "$STATE_FILE")
  PROGRESS=$(echo "scale=1; $COMPLETED * 100 / $TOTAL_PERSONAS" | bc)
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Progress: $PROGRESS% ($COMPLETED/$TOTAL_PERSONAS)"

  # Rate limiting (avoid Claude API rate limits: 90 requests/min)
  sleep 1  # 1 persona per second = 60/min (safe buffer)
done

# Generate completion report
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Generating batch completion report..."
$PYTHON_BIN "$GENERATOR_SCRIPT" --generate-report

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Batch 1 production complete!"
```

### 4.2 Parallel Processing (Optional)

**GNU Parallel Integration**:
```bash
# Install GNU Parallel (if not available)
# sudo apt-get install parallel

# Run 4 personas in parallel (respect Claude API rate limit: 90 req/min)
cat batch1_config.json | jq -r '.personas[] | @base64' | \
  parallel -j 4 --delay 1 \
  "$PYTHON_BIN $GENERATOR_SCRIPT --persona {}"
```

**Note**: Parallel processing increases throughput but requires careful rate limit management to avoid Claude API throttling (90 requests/min limit).

---

## 5. Monitoring & Progress Tracking

### 5.1 Real-Time Dashboard

**Dashboard File** (`batch1_progress_dashboard.md`):
```markdown
# Batch 1 Production Progress Dashboard

**Last Updated**: 2026-03-15 14:32:18 (auto-updates every 60 seconds)

---

## Overall Progress

**Completed**: 142/207 personas (68.6%)
**Failed**: 3 personas (flagged for manual review)
**In Progress**: 1 persona
**Pending**: 61 personas

**Estimated Completion**: 2026-03-15 18:45:00 (4h 13m remaining)

---

## Specialty Breakdown

| Specialty | Completed | Total | Progress |
|-----------|-----------|-------|----------|
| Cardiology | 32/45 | 71.1% | ████████████████░░░░░░░░ |
| Emergency | 28/45 | 62.2% | ████████████████░░░░░░░░ |
| General Practice | 45/54 | 83.3% | ████████████████████░░░░ |
| Pediatrics | 24/36 | 66.7% | ████████████████░░░░░░░░ |
| Respiratory | 13/27 | 48.1% | ████████████░░░░░░░░░░░░ |

---

## Quality Metrics

**QA Validation**:
- Average Deployment Readiness: 100.0%
- QA Pass Rate (first attempt): 94.2%
- Average Retry Count: 1.08

**Clinical Validation**:
- Average Clinical Accuracy Score: 9.14/10
- Clinical Approval Rate: 100%
- Average FRACP Review Score: 9.05/10

**Performance**:
- Average Time per Persona: 18.7 seconds
- Success Rate: 98.6%
- API Error Rate: 0.5%

---

## Recent Activity (Last 10 Personas)

| Persona ID | Status | Attempts | Score | Timestamp |
|------------|--------|----------|-------|-----------|
| gp_045_menopause_female_52 | ✅ Completed | 1 | 9.3/10 | 14:32:05 |
| pediatrics_024_febrile_seizure_male_2 | ✅ Completed | 2 | 8.9/10 | 14:31:42 |
| cardiology_032_pe_female_45 | ✅ Completed | 1 | 9.5/10 | 14:31:18 |
| ... | ... | ... | ... | ... |

---

## Flagged for Manual Review (3 personas)

| Persona ID | Reason | Last Error |
|------------|--------|------------|
| emergency_018_meningitis_male_8 | QA validation failed | RAG citation confidence 0.59 < 0.65 (3 attempts) |
| respiratory_007_ild_female_68 | Clinical validation failed | Clinical accuracy 7.8/10 < 8.0 threshold |
| cardiology_021_hocm_male_32 | Timeout | Claude API timeout after 60s (3 attempts) |

---

**Dashboard Auto-Updates**: This file updates every 60 seconds during Ralph loop execution.
```

### 5.2 Logging

**Log Levels**:
- `INFO`: Normal operation (persona started, completed)
- `WARNING`: Retry attempts, auto-fix applied
- `ERROR`: Generation failed, validation failed
- `CRITICAL`: System error, API unavailable

**Log Format**:
```
[2026-03-15 14:32:18] [INFO] [cardiology_032] Generating persona: PE, Medium difficulty, Female 45yo
[2026-03-15 14:32:35] [INFO] [cardiology_032] QA validation: 10/13 gates passed, 100% deployment ready
[2026-03-15 14:32:48] [INFO] [cardiology_032] Clinical validation: 9.5/10, approved
[2026-03-15 14:32:50] [INFO] [cardiology_032] ✅ Persona completed successfully (attempt 1, 32 seconds)
```

---

## 6. Acceptance Criteria

### 6.1 Functional Requirements

| Requirement | Acceptance Criteria | Status |
|-------------|---------------------|--------|
| **FR-1: Automated Generation** | Generate 207 personas automatically via Claude API | To Test |
| **FR-2: Quality Gates** | All personas pass 10/13 QA gates (100% deployment readiness) | To Test |
| **FR-3: Clinical Validation** | All personas achieve clinical accuracy ≥8.0/10 | To Test |
| **FR-4: Error Handling** | Retry failed personas up to 3 times with exponential backoff | To Test |
| **FR-5: State Persistence** | Resume from failure without losing progress | To Test |
| **FR-6: Progress Tracking** | Real-time dashboard updates every 60 seconds | To Test |

### 6.2 Non-Functional Requirements

| Requirement | Acceptance Criteria | Target |
|-------------|---------------------|--------|
| **NFR-1: Performance** | Average time per persona | <30 seconds |
| **NFR-2: Success Rate** | Percentage of personas passing validation on first attempt | >90% |
| **NFR-3: Cost** | Total Claude API cost for 207 personas | <$20 |
| **NFR-4: Reliability** | System uptime during batch execution | >99% |
| **NFR-5: Scalability** | Support for parallel processing (future batches) | 4-8 parallel processes |

### 6.3 Quality Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Average Clinical Accuracy** | ≥8.5/10 | Mean score across all personas |
| **QA Pass Rate** | 100% | Personas with deployment_readiness = 100% |
| **RAG Citation Quality** | >0.65 confidence | Average confidence score |
| **Security Violations** | 0 | Zero hardcoded credentials or PHI leaks |
| **FRACP Approval Rate** | 100% | All personas have 2 approved FRACP reviews |

---

## 7. Testing Plan

### 7.1 Unit Testing

**Test Persona Generation**:
```python
def test_generate_persona_cardiology_stemi():
    """Test persona generation for cardiology STEMI"""
    config = {
        "specialty": "Cardiology",
        "diagnosis": "STEMI (inferior wall)",
        "difficulty": "Medium",
        "demographics": {"age": 65, "gender": "Male", "name": "John Test"}
    }

    persona = generate_persona(config)

    # Assert required fields present
    assert "id" in persona
    assert persona["specialty"] == "Cardiology"
    assert persona["difficulty"] == "Medium"

    # Assert symptoms have RAG citations
    assert len(persona["symptoms"]) >= 3
    for symptom in persona["symptoms"]:
        assert "rag_citation" in symptom
        assert symptom["rag_citation"]["confidence"] > 0.65

    # Assert FRACP reviews approved
    assert len(persona["fracp_reviews"]) == 2
    for review in persona["fracp_reviews"]:
        assert review["approved"] == True
```

### 7.2 Integration Testing

**Test Ralph Loop (3 Sample Personas)**:
```bash
# Create mini-batch config (3 personas)
cat > batch1_config_test.json <<EOF
{
  "total_personas": 3,
  "personas": [
    {"specialty": "Cardiology", "diagnosis": "STEMI", "difficulty": "Medium"},
    {"specialty": "Emergency", "diagnosis": "Anaphylaxis", "difficulty": "Medium"},
    {"specialty": "General Practice", "diagnosis": "Type 2 Diabetes", "difficulty": "Easy"}
  ]
}
EOF

# Run Ralph loop on test batch
./ralph-batch1-loop.sh --config batch1_config_test.json

# Verify all 3 personas generated and validated
assert_equal $(jq -r '.completed_personas' .batch1_state.json) 3
assert_equal $(find batch1-output -name "*_pilot.json" | wc -l) 3
assert_equal $(find batch1-output -name "*_qa_report.json" | wc -l) 3
```

### 7.3 Acceptance Testing

**User Acceptance Criteria**:
1. ✅ User can start Ralph loop with single command: `./ralph-batch1-loop.sh`
2. ✅ User can resume after interruption: `./ralph-batch1-loop.sh --resume`
3. ✅ User can monitor progress in real-time via dashboard file
4. ✅ User receives completion report with aggregate statistics
5. ✅ All personas are deployment-ready (100% validation)

---

## 8. Risk Management

### 8.1 Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Claude API Rate Limit Exceeded** | Medium | High | Implement rate limiting (1 req/sec), exponential backoff |
| **API Timeout/Downtime** | Low | Medium | Retry logic (3 attempts), state persistence (resume later) |
| **Low-Quality Personas Generated** | Medium | High | Multi-layered validation (syntax → QA → clinical), auto-fix patterns |
| **Insufficient RAG Citations** | Medium | Medium | Enforce >0.65 confidence threshold, regenerate if below |
| **Security Violations** | Low | Critical | Automated security scan (credentials, PHI), zero-tolerance policy |
| **Disk Space Exhaustion** | Low | Low | Monitor disk usage (207 personas × ~10KB each = ~2MB total) |

### 8.2 Contingency Plans

**If Claude API becomes unavailable**:
1. Pause Ralph loop execution
2. Save current state to `batch1_state.json`
3. Resume when API recovers using `--resume` flag
4. No data loss (stateful resumption)

**If QA validation consistently fails**:
1. Analyze common failure patterns (e.g., specific specialty, difficulty level)
2. Adjust persona generation prompt template
3. Re-run failed personas
4. Manual review for systematic issues

**If timeline at risk (>1 week)**:
1. Enable parallel processing: `--parallel 4` (respect rate limits)
2. Extend working hours (run overnight)
3. Prioritize high-value specialties (Cardiology, Emergency first)

---

## 9. Success Metrics

### 9.1 Primary Metrics

| Metric | Baseline (Phase 2) | Target (Phase 3) | Measurement |
|--------|-------------------|------------------|-------------|
| **Deployment Readiness** | 100% (10/10 personas) | 100% (207/207 personas) | QA validation reports |
| **Average Clinical Accuracy** | 9.1/10 | ≥8.5/10 | Clinical validation reports |
| **Cost per Persona** | $0.02 | <$0.10 | Claude API usage logs |
| **Time per Persona** | ~30 min (manual) | <30 sec (automated) | State file timestamps |

### 9.2 Secondary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **First-Attempt Success Rate** | >90% | Personas passing without retry |
| **Auto-Fix Success Rate** | >70% | Common errors auto-fixed vs manual review |
| **API Error Rate** | <2% | Timeouts, rate limits, API errors |
| **State Recovery Success** | 100% | Resume from failure without data loss |

---

## 10. Deliverables

### 10.1 Code Deliverables

| File | Purpose | Status |
|------|---------|--------|
| `ralph-batch1-loop.sh` | Main Ralph loop automation script | Ready for Implementation |
| `batch1_persona_generator.py` | Claude API persona generation | Ready for Implementation |
| `batch1_config.json` | 207 persona specifications | Ready for Implementation |
| `batch1_validation_gates.py` | Quality gates enforcement | Ready for Implementation |
| `batch1_error_handler.py` | Error handling and retry logic | Ready for Implementation |
| `batch1_progress_tracker.py` | Real-time dashboard generator | Ready for Implementation |

### 10.2 Documentation Deliverables

| Document | Purpose | Status |
|----------|---------|--------|
| `BATCH_1_USAGE_GUIDE.md` | Step-by-step user guide | Ready for Implementation |
| `BATCH_1_COMPLETION_REPORT.md` | Final batch statistics and analysis | Generated post-execution |
| `BATCH_1_TROUBLESHOOTING.md` | Common errors and solutions | Ready for Implementation |

### 10.3 Data Deliverables

| Output | Format | Count |
|--------|--------|-------|
| **Persona JSON Files** | `.json` | 207 files |
| **QA Validation Reports** | `.json` | 207 files |
| **Clinical Validation Reports** | `.json` | 207 files |
| **Batch State File** | `.json` | 1 file (final state) |
| **Completion Report** | `.md` | 1 file |

---

## 11. Timeline

### 11.1 Estimated Timeline (5 Business Days)

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| **Day 1** | Setup Ralph loop infrastructure, create config files | Scripts + config ready for testing |
| **Day 2** | Test Ralph loop with 10 sample personas, iterate on errors | 10 validated personas |
| **Day 3** | Run Batch 1 production (207 personas), monitor progress | ~150 personas generated |
| **Day 4** | Complete remaining personas, manual review of flagged personas | All 207 personas validated |
| **Day 5** | Generate completion report, prepare for PostgreSQL import | Batch 1 complete, ready for deployment |

### 11.2 Detailed Schedule

**Week 1 (2026-03-16 to 2026-03-20)**:
- Monday 03-16: Implementation Day (create all scripts, test with 3 personas)
- Tuesday 03-17: Pilot Run (50 personas, validate system stability)
- Wednesday 03-18: Full Production Start (run overnight for 24h continuous generation)
- Thursday 03-19: Complete remaining personas, manual review
- Friday 03-20: Generate completion report, hand off to Phase 3B (PostgreSQL import)

---

## 12. Next Steps (Phase 3B - Database Import)

After Batch 1 completion, proceed to:

1. **PostgreSQL Import**:
   - Import 207 validated personas to `patient_personas` table
   - Link QA reports to `qa_validations` table
   - Link clinical reports to `clinical_validations` table

2. **Deployment View Query**:
   ```sql
   SELECT * FROM deployment_ready_personas
   WHERE clinical_accuracy_score >= 8.0
     AND deployment_readiness = 100.0
   ORDER BY specialty, difficulty;
   ```

3. **Frontend Integration**:
   - Update irStudy backend API to serve personas
   - Frontend UI to display personas in AI OSCE practice interface

4. **Batch 2 Planning** (153 personas):
   - Specialties: ObGyn (27), Surgery (27), Psychiatry (27), Infectious Diseases (27), Neurology (45)
   - Apply lessons learned from Batch 1

---

**PRD Status**: ✅ **READY FOR IMPLEMENTATION**
**Approval Required**: Clinical Content Team Lead
**Next Action**: Begin implementation (create scripts and config files)

---

**Document Version**: 1.0
**Last Updated**: 2026-03-15
**Next Review**: 2026-03-20 (post-Batch 1 completion)
