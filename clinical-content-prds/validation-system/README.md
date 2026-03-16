# AI-Powered Persona Validation System

**Created**: 2026-03-15
**Purpose**: Complete QA validation system for 360 AI patient personas
**Architecture**: 3-layer validation (Clinical → QA → Deployment)

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ LAYER 1: PERSONA CREATION (MED-001 to MED-010)             │
│ → Claude Skills create personas with RAG citations          │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ LAYER 2: CLINICAL VALIDATION (claude_validator.py)          │
│ → FRACP-VALIDATOR-001 to 010 via Claude API                 │
│ → Scores 0-10 (8 clinical criteria)                         │
│ → PASS if ≥8.0/10                                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ LAYER 3: TECHNICAL QA VALIDATION (qa_validator.py)          │
│ → 13 quality gates (JSON, RAG, security, cultural safety)   │
│ → PASS if 100% gates passed                                 │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ DEPLOYMENT (PostgreSQL Database)                            │
│ → Stores personas + validation reports                      │
│ → Ready for production AI OSCE system                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 Files Overview

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| **qa_validator.py** | Technical QA validation (13 quality gates) | 582 | ✅ Ready |
| **claude_validator.py** | Claude API integration for FRACP validators | 187 | ✅ Ready |
| **validation_pipeline.py** | End-to-end pipeline orchestration | 234 | ✅ Ready |
| **database_schema.sql** | PostgreSQL schema for personas + reports | 250 | ✅ Ready |
| **test_persona_stemi.json** | Sample STEMI cardiology persona for testing | 228 | ✅ Ready |
| **README.md** | This file | - | ✅ Ready |

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
pip install anthropic  # Claude API client
```

### **2. Set Claude API Key**

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### **3. Test QA Validation** (No API calls)

```bash
python qa_validator.py test_persona_stemi.json
```

**Expected Output**:
```
==============================================================
QA VALIDATION REPORT
==============================================================
Persona ID: cardiology_001_stemi_male_65
Gates Passed: 13/13
Gates Failed: 0
Deployment Readiness: 100.0%
Recommendation: APPROVED FOR DEPLOYMENT

Full report written to: test_persona_stemi_qa_report.json
==============================================================
```

### **4. Test Clinical Validation** (Claude API call)

```bash
python claude_validator.py test_persona_stemi.json Cardiology
```

**Expected Output**:
```
==============================================================
FRACP CLINICAL VALIDATION REPORT - Cardiology
==============================================================
Validator: FRACP-VALIDATOR-001
Persona ID: cardiology_001_stemi_male_65
Clinical Accuracy Score: 9.2/10
Approval: True
Recommendation: APPROVED - Excellent cardiology persona

STRENGTHS:
  ✅ Classic STEMI presentation with all key features
  ✅ Evidence-based management aligned with eTG 2.1
  ✅ Excellent 9-step history with SOCRATES framework
  ✅ Australian medical context well integrated (PBS, eTG)

IMPROVEMENTS:
  💡 Consider adding GRACE score for risk stratification

Full report written to: test_persona_stemi_clinical_validation.json
==============================================================
```

### **5. Run Complete Pipeline** (Both validations)

```bash
python validation_pipeline.py test_persona_stemi.json Cardiology
```

**Expected Output**:
```
======================================================================
VALIDATION PIPELINE: cardiology_001_stemi_male_65
======================================================================

[STEP 1/3] Clinical Validation (Cardiology)...
  ✓ Clinical Validation Complete
    Score: 9.2/10
    Status: ✅ APPROVED

[STEP 2/3] Technical QA Validation (13 quality gates)...
  ✓ QA Validation Complete
    Gates Passed: 13/13
    Deployment Readiness: 100.0%
    Status: ✅ APPROVED

[STEP 3/3] Deployment Decision...
  ✅ APPROVED FOR DEPLOYMENT

  📄 Reports saved:
     ./validation-output/cardiology_001_stemi_male_65_clinical_validation_20260315_103045.json
     ./validation-output/cardiology_001_stemi_male_65_qa_validation_20260315_103046.json

======================================================================
PIPELINE SUMMARY
======================================================================
Clinical Validation: ✅ PASS (9.2/10)
QA Validation: ✅ PASS (13/13 gates)
Deployment Status: ✅ APPROVED
======================================================================
```

---

## 📋 QA Validation (13 Quality Gates)

**Implemented in**: `qa_validator.py`

| Gate | Check | Pass Criteria |
|------|-------|---------------|
| **1. JSON Compliance** | All required fields present | 17 required fields |
| **2. RAG Citations >0.65** | eTG/AMH citations with confidence >0.65 | All symptoms cited |
| **3. ≥2 FRACP Reviews** | At least 2 approved reviews | Both approved |
| **4. Clinical Accuracy** | No dangerous advice | No contraindications |
| **5. Australian Context** | PBS/MBS, no US terms | Paracetamol NOT acetaminophen |
| **6. Difficulty Appropriate** | Complexity matches Easy/Medium/Hard | Symptoms/comorbidities align |
| **7. Specialty Valid** | Specialty in valid list | 10 specialties |
| **8. Cultural Safety - Aboriginal** | Nation specified, no stereotypes | Cultural liaison review |
| **9. Cultural Safety - LGBTQIA+** | Correct pronouns, no misgendering | Educator review |
| **10. Cultural Safety - CALD** | Interpreter services, diverse | No stereotypes |
| **11. Zero Credentials** | No API keys, passwords | Security scan |
| **12. Zero Security Violations** | PHI anonymized | No real patient data |
| **13. Educational Alignment** | 9-step history, SOCRATES | AMC competencies |

---

## 🧪 Clinical Validation (8 Criteria)

**Implemented in**: `claude_validator.py` (invokes FRACP-VALIDATOR-001 to 010 via Claude API)

| Criterion | Weight | Check |
|-----------|--------|-------|
| **1. Diagnosis Accuracy** | 2.0 pts | Diagnosis matches presentation |
| **2. Management Appropriateness** | 2.0 pts | Evidence-based, eTG-aligned |
| **3. Australian Medical Context** | 1.0 pt | PBS/MBS/eTG, no US terms |
| **4. Difficulty Appropriateness** | 1.0 pt | Complexity matches difficulty |
| **5. Critical Errors Defined** | 1.0 pt | Auto-fail scenarios appropriate |
| **6. RAG Citations Quality** | 1.0 pt | Correct eTG sections, >0.65 confidence |
| **7. 9-Step History Structure** | 1.0 pt | SOCRATES framework, all steps |
| **8. Red Flags Identified** | 1.0 pt | Life-threatening features flagged |

**Total**: 10.0 points
**Pass Threshold**: ≥8.0/10

---

## 💾 Database Schema

**File**: `database_schema.sql` (PostgreSQL)

### **Tables**:

1. **`patient_personas`**: Stores personas with metadata
   - Primary key: `id` (e.g., "cardiology_001_stemi_male_65")
   - Full persona JSON in `persona_json` JSONB column
   - Validation status fields
   - Cultural diversity flags

2. **`clinical_validations`**: Stores FRACP validator reports
   - Foreign key to `patient_personas.id`
   - Clinical accuracy score (0-10)
   - Full validation report JSON

3. **`qa_validations`**: Stores QA-001 reports
   - Foreign key to `patient_personas.id`
   - Quality gates results (13 gates)
   - Deployment readiness percentage

### **Views**:

- `deployment_ready_personas`: Personas approved for deployment
- `validation_summary`: Validation statistics by specialty/difficulty

### **Setup**:

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d irstudy_medical

# Create schema
\i database_schema.sql
```

---

## 🧩 Integration with Existing irStudy System

### **Backend Integration** (FastAPI)

```python
# backend/src/api/v1/personas.py

from validation_system.validation_pipeline import ValidationPipeline

@router.post("/personas/validate")
async def validate_persona(persona: PersonaCreate, specialty: str):
    """
    Validate persona through complete pipeline
    """
    pipeline = ValidationPipeline()
    summary = pipeline.run_pipeline(persona.dict(), specialty)

    return summary
```

### **Database Integration**

```python
# backend/src/db/models.py

from sqlalchemy import Column, String, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB

class PatientPersona(Base):
    __tablename__ = "patient_personas"

    id = Column(String(100), primary_key=True)
    specialty = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=False)
    persona_json = Column(JSONB, nullable=False)
    clinical_validation_status = Column(String(20), default="pending")
    qa_validation_status = Column(String(20), default="pending")
    deployment_status = Column(String(20), default="draft")
```

---

## 📊 Usage Examples

### **Example 1: Validate Single Persona**

```bash
# QA validation only (fast, no API calls)
python qa_validator.py my_persona.json

# Clinical validation (Claude API call)
python claude_validator.py my_persona.json Cardiology

# Complete pipeline (both)
python validation_pipeline.py my_persona.json Cardiology
```

### **Example 2: Batch Validation** (10 Personas)

```bash
for file in personas/*.json; do
  specialty=$(basename "$file" | cut -d'_' -f1)
  python validation_pipeline.py "$file" "$specialty"
done
```

### **Example 3: Query Database** (Deployment-Ready Personas)

```sql
-- Get all deployment-ready personas
SELECT * FROM deployment_ready_personas
ORDER BY specialty, difficulty;

-- Validation summary by specialty
SELECT * FROM validation_summary;

-- Personas needing revision
SELECT p.id, p.specialty, cv.clinical_accuracy_score, cv.feedback
FROM patient_personas p
JOIN clinical_validations cv ON p.id = cv.persona_id
WHERE cv.overall_approval = FALSE
ORDER BY cv.validated_at DESC;
```

---

## ✅ Success Criteria

**Persona APPROVED FOR DEPLOYMENT when**:
- ✅ Clinical validation: Score ≥8.0/10 (FRACP-equivalent approval)
- ✅ QA validation: 13/13 quality gates passed (100%)
- ✅ No critical errors detected
- ✅ No security violations (credentials, PHI)

**If Rejected**:
- Return to persona creator (MED-001 to MED-010)
- Fix issues based on validation feedback
- Re-validate until approved

---

## 🎯 Next Steps

1. **Test with Pilot Persona** (Done ✅):
   ```bash
   python validation_pipeline.py test_persona_stemi.json Cardiology
   ```

2. **Create 10 Pilot Personas** (Phase 2):
   - 1 per specialty (Cardiology, Emergency, GP, etc.)
   - Validate each through complete pipeline
   - Iterate based on AI validator feedback

3. **Scale to Batch Production** (Phase 3-6):
   - Use Ralph loop or batch script
   - Validate 207 personas (Batch 1)
   - Then 153 personas (Batch 2)
   - Then 60 physical exam personas
   - Then 92 cultural diversity personas

4. **Deploy to Production** (Phase 7):
   - Import approved personas to PostgreSQL
   - Integrate with AI OSCE frontend
   - Launch platform with 360 validated personas

---

## 📈 Performance Metrics

**Speed**:
- QA validation: ~1 second per persona (Python code)
- Clinical validation: ~10-15 seconds per persona (Claude API call)
- Complete pipeline: ~20 seconds per persona

**Throughput**:
- Single persona: 20 seconds
- 10 personas (sequential): 3-4 minutes
- 360 personas (parallel): ~2 hours (with sufficient API rate limits)

**Cost**:
- QA validation: $0 (local Python)
- Clinical validation: ~$0.02 per persona (Claude API)
- 360 personas: ~$7.20 total (vs $9,900 FRACP panel)

---

**Status**: ✅ **COMPLETE VALIDATION SYSTEM READY**
**Last Updated**: 2026-03-15
**Version**: 1.0
