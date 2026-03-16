# PRD-RALPH-002: Generate Full 207-Persona Configuration

**Created**: 2026-03-15
**Priority**: P0 (Critical)
**Status**: Ready for Execution
**Estimated Duration**: 30 minutes (automated)

---

## Executive Summary

Generate complete batch1_full_config.json with all 207 FRACP-equivalent persona specifications, organized by specialty and difficulty level, ready for production batch generation.

---

## Business Requirements

### BR-001: Scale from Pilot to Production
- **Current**: 25 personas (pilot validation)
- **Target**: 207 personas (production deployment)
- **Purpose**: Comprehensive AMC Clinical Exam preparation coverage

### BR-002: Specialty Coverage
Meet PRD-003 distribution requirements:
- Cardiology: 45 personas
- Emergency: 45 personas
- General Practice: 54 personas
- Pediatrics: 36 personas
- Respiratory: 27 personas

### BR-003: Difficulty Balance
- Easy: 62 personas (30% - straightforward, <2 comorbidities)
- Medium: 124 personas (60% - complex or time-critical, 2-4 comorbidities)
- Hard: 21 personas (10% - rare/multi-organ, >4 comorbidities)

---

## Functional Requirements

### FR-001: Config File Structure
**File**: `batch1_full_config.json`
**Location**: `clinical-content-prds/validation-system/`

**Required Fields**:
```json
{
  "batch_id": "batch_1_production",
  "total_personas": 207,
  "specialties": {
    "Cardiology": 45,
    "Emergency": 45,
    "General Practice": 54,
    "Pediatrics": 36,
    "Respiratory": 27
  },
  "difficulty_distribution": {
    "Easy": 62,
    "Medium": 124,
    "Hard": 21
  },
  "personas": [ ... 207 specifications ... ],
  "name_patterns": { ... },
  "metadata": { ... }
}
```

### FR-002: Persona Specification Format
**Each persona entry must include**:
```json
{
  "id": "{specialty}_{seq}_{diagnosis_abbrev}_{gender}_{age}",
  "specialty": "Cardiology|Emergency|General Practice|Pediatrics|Respiratory",
  "diagnosis": "Full diagnosis name with severity/type",
  "difficulty": "Easy|Medium|Hard",
  "demographics": {
    "age": 0-100,
    "gender": "Male|Female",
    "name_pattern": "common_male|common_female|pediatric_male|pediatric_female"
  }
}
```

### FR-003: Diagnosis Variety Requirements

#### Cardiology (45 personas)
**Acute Coronary Syndromes** (15):
- STEMI: inferior (3), anterior (3), lateral (2)
- NSTEMI: high-risk (3), intermediate-risk (2)
- Unstable angina (2)

**Arrhythmias** (10):
- Atrial fibrillation: new onset (3), chronic (2), RVR (2)
- SVT (1), VT (1), Heart block (1)

**Heart Failure** (8):
- Acute decompensated (3), Chronic stable (2)
- Cardiogenic shock (1), Right-sided HF (2)

**Valvular/Structural** (7):
- Aortic stenosis (2), Mitral regurgitation (2)
- Infective endocarditis (1), Pericarditis (1), Myocarditis (1)

**Vascular** (5):
- Pulmonary embolism (2), Aortic dissection (1), DVT (2)

#### Emergency (45 personas)
**Anaphylaxis/Allergic** (5):
- Food allergy (2), Drug reaction (2), Insect sting (1)

**Sepsis/Shock** (8):
- Septic shock (3), Hypovolemic shock (2), Cardiogenic shock (2), Neurogenic shock (1)

**Trauma** (7):
- Major trauma MVC (2), Fall from height (2), Penetrating trauma (1), Head injury (2)

**Poisoning/Toxicology** (6):
- Paracetamol overdose (2), TCA overdose (1), Organophosphate (1), Carbon monoxide (1), Alcohol intoxication (1)

**Acute Abdomen** (8):
- Perforated peptic ulcer (2), Bowel obstruction (2), Ectopic pregnancy (2), Acute pancreatitis (2)

**Neurological Emergencies** (6):
- Status epilepticus (2), Stroke (ischemic 2, hemorrhagic 1), Meningitis (1)

**Metabolic Emergencies** (5):
- DKA (2), HHS (1), Hypoglycemia (1), Addisonian crisis (1)

#### General Practice (54 personas)
**Chronic Disease Management** (20):
- Type 2 Diabetes: new diagnosis (4), suboptimal control (4), complications (2)
- Hypertension: new diagnosis (3), resistant (2), with complications (2)
- CKD: stage 3 (2), stage 4 (1)

**Mental Health** (12):
- Depression: mild (2), moderate (3), severe (2)
- Anxiety: GAD (2), panic disorder (2), social anxiety (1)

**Musculoskeletal** (8):
- Chronic low back pain (3), Osteoarthritis (2), Rheumatoid arthritis (1), Gout (2)

**Gastrointestinal** (6):
- GORD (2), IBS (2), Chronic constipation (1), Peptic ulcer (1)

**Preventive Health** (4):
- Health assessment (2), Immunization (1), Cancer screening (1)

**Women's Health** (4):
- Menopause (2), PCOS (1), Contraception counseling (1)

#### Pediatrics (36 personas)
**Infectious Diseases** (15):
- Acute otitis media (3), Viral URTI (3), Gastroenteritis (3)
- Bronchiolitis (2), Croup (2), Pneumonia (2)

**Respiratory** (8):
- Asthma: acute exacerbation (3), newly diagnosed (2)
- Wheeze (first episode) (2), Chronic cough (1)

**Neurological** (5):
- Febrile seizure: simple (2), complex (1)
- Developmental delay (1), Headache (1)

**Neonatal** (4):
- Neonatal jaundice (2), Poor feeding (1), Sepsis evaluation (1)

**Other** (4):
- Immunization visit (1), Failure to thrive (1), Abdominal pain (1), Rash (1)

#### Respiratory (27 personas)
**COPD** (9):
- Exacerbation: Type 1 (3), Type 2 (2), Type 3 (2)
- COPD with cor pulmonale (1), Alpha-1 antitrypsin deficiency (1)

**Pneumonia** (6):
- CAP: mild (2), severe (2), aspiration (2)

**Asthma** (5):
- Acute severe (2), Life-threatening (1), Brittle asthma (1), Exercise-induced (1)

**Pulmonary Embolism** (3):
- Massive PE (1), Subsegmental PE (1), Recurrent PE (1)

**Pleural Disease** (2):
- Pleural effusion: parapneumonic (1), malignant (1)

**Other** (2):
- Pneumothorax (1), Interstitial lung disease (1)

### FR-004: Demographics Distribution

**Age Appropriateness**:
- Cardiology: 45-85 years (median 65)
- Emergency: 18-85 years (wide range)
- General Practice: 25-75 years (median 55)
- Pediatrics: 0-18 years (infants, children, adolescents)
- Respiratory: 35-80 years (median 65)

**Gender Balance**:
- Overall: ~50% male, ~50% female
- Adjust for diagnosis epidemiology (e.g., ectopic pregnancy = female only)

**Name Patterns**:
- Adults: common_male / common_female (Australian names)
- Pediatrics: pediatric_male / pediatric_female

---

## Implementation Approach

### Option A: Automated Generation (Recommended)
**Use Claude API to generate config**:
1. Create Python script: `generate_full_config.py`
2. Use Claude Sonnet 4.5 with structured prompt
3. Validate output against schema
4. Save to batch1_full_config.json

**Advantages**:
- Fast (5 minutes total)
- Ensures variety and medical accuracy
- Validates against PRD requirements

### Option B: Manual Template Expansion
**Manually create 207 entries**:
1. Copy batch1_config.json structure
2. Add diagnoses following FR-003 breakdown
3. Manually assign demographics

**Disadvantages**:
- Time-consuming (2-3 hours)
- Error-prone
- Tedious

**Decision**: ✅ Use Option A (Automated Generation)

---

## Acceptance Criteria

### AC-001: File Structure Valid
- ✅ Valid JSON format (no syntax errors)
- ✅ `total_personas: 207`
- ✅ All required top-level fields present

### AC-002: Persona Count Correct
- ✅ Exactly 207 persona entries in `personas` array
- ✅ Specialty distribution: Cardiology (45), Emergency (45), GP (54), Pediatrics (36), Respiratory (27)
- ✅ Difficulty distribution: Easy (62), Medium (124), Hard (21)

### AC-003: Persona Specifications Complete
- ✅ All 207 personas have unique IDs
- ✅ All have valid specialty codes
- ✅ All have appropriate diagnoses
- ✅ All have age-appropriate demographics

### AC-004: Diagnosis Variety
- ✅ No duplicate diagnoses (207 unique clinical scenarios)
- ✅ Diagnosis variety meets FR-003 breakdown
- ✅ Clinical realism (diagnoses match specialty/age/difficulty)

---

## Validation Steps

### V-001: Schema Validation
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('batch1_full_config.json'))"
# Expected: No errors

# Check total count
jq '.total_personas' batch1_full_config.json
# Expected: 207

# Check personas array length
jq '.personas | length' batch1_full_config.json
# Expected: 207
```

### V-002: Distribution Validation
```bash
# Check specialty distribution
jq '.personas | group_by(.specialty) | map({specialty: .[0].specialty, count: length})' batch1_full_config.json
# Expected: Cardiology:45, Emergency:45, GP:54, Pediatrics:36, Respiratory:27

# Check difficulty distribution
jq '.personas | group_by(.difficulty) | map({difficulty: .[0].difficulty, count: length})' batch1_full_config.json
# Expected: Easy:62, Medium:124, Hard:21
```

### V-003: Uniqueness Validation
```bash
# Check for duplicate IDs
jq '.personas | map(.id) | group_by(.) | map(select(length > 1))' batch1_full_config.json
# Expected: [] (empty array = no duplicates)

# Check for duplicate diagnoses
jq '.personas | map(.diagnosis) | group_by(.) | map(select(length > 1)) | length' batch1_full_config.json
# Expected: <50 (some diagnoses repeated with variations is OK)
```

---

## Deliverables

### D-001: Full Configuration File
**File**: `batch1_full_config.json`
**Location**: `clinical-content-prds/validation-system/`
**Size**: ~150-200 KB (207 persona specs)

### D-002: Validation Report
**Contents**:
- Total personas: 207 ✅
- Specialty distribution verified ✅
- Difficulty distribution verified ✅
- Unique IDs: 207 ✅
- Schema valid ✅

---

## Dependencies

- ✅ PRD-003_BATCH_1_PRODUCTION.md (source specifications)
- ✅ batch1_config.json (template/example structure)
- ✅ Claude CLI or Python anthropic SDK (for automated generation)

---

## Timeline

**Total Estimated Duration**: 30 minutes

| Task | Duration |
|------|----------|
| Create generation script | 10 min |
| Run automated generation | 5 min |
| Validation checks | 10 min |
| Manual review/adjustments | 5 min |

**Expected Completion**: 2026-03-15 13:40

---

## Risk Mitigation

### Risk 1: Diagnosis Repetition
**Probability**: Medium
**Impact**: Low
**Mitigation**: Validate uniqueness, add severity/type variations

### Risk 2: Demographics Mismatch
**Probability**: Low
**Impact**: Low
**Mitigation**: Age ranges validated per specialty

### Risk 3: Distribution Errors
**Probability**: Low
**Impact**: Medium
**Mitigation**: Automated validation scripts (V-002)

---

## Post-Completion Actions

1. **Archive pilot config**: Rename batch1_config.json → batch1_pilot_config.json
2. **Set as default**: Copy batch1_full_config.json → batch1_config.json
3. **Update state file**: Reset .batch1_state.json for 207 personas
4. **Proceed to PRD-RALPH-003**: Execute full 207-persona batch

---

**Status**: ✅ READY FOR EXECUTION
**Next PRD**: PRD-RALPH-003 (Run Full 207 Batch)
**Owner**: Ralph Automation System
**Approver**: Clinical Content PRD Team
