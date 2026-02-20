# PRD_BACKEND_004: OSCE→EMR Patient Scenario Converter

**PRD ID**: PRD_BACKEND_004
**Title**: OSCE to EMR Mock Patient Converter
**Category**: Backend - Data Generation
**Priority**: P0-Critical (blocks patient content availability)
**Owner**: Backend Engineer + NLP Specialist
**Estimated Effort**: 10-14 hours
**Dependencies**: PRD_BACKEND_001 (Database Migration)
**Blocks**: All EMR practice functionality (needs patient scenarios)

**Created**: 2026-02-16
**Status**: Ready for Implementation

---

## R - REQUEST (What and Why)

### User Story

**AS A** backend engineer building the EMR Practice System
**I WANT TO** automatically convert 221 existing OSCE scenarios into 500+ comprehensive mock patient records
**SO THAT** students have diverse, Australian-compliant patient scenarios for EMR documentation practice without manual data entry

### Business Context

**Current State**:
- 221 OSCE scenarios exist in the `osces` table with rich clinical content
- Each OSCE has `patient_instructions`, `examiner_checklist`, `vital_signs` in JSONB
- NO mock patient records exist for EMR practice
- Manual creation of 500+ patients would take 200+ hours (unacceptable)
- American-centric patient data generators don't meet Australian standards

**Problem**:
- EMR system needs realistic patient scenarios (names, Medicare numbers, MRN, allergies, medications)
- OSCE data contains clinical information but not structured patient demographics
- Australian-specific data (Medicare format, Aboriginal/TSI status, PBS medications) must be generated
- Need 500+ unique patients for practice variety (multiple students, repeated practice)

**Desired State**:
- Automated NLP parser extracts clinical data from OSCE text
- Australian data generator creates compliant demographics
- 221 OSCEs → 500+ mock patients (some OSCEs spawn multiple patient variations)
- All patients ready for EMR session assignment
- Batch conversion script runs in <10 minutes

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Patient Generation** | 500+ unique patients | `SELECT COUNT(*) FROM mock_patients` ≥ 500 |
| **Australian Compliance** | 100% valid Medicare numbers | Regex validation + check digit |
| **Clinical Accuracy** | 95% OSCE data extraction accuracy | Manual review of 50 random patients |
| **Performance** | Conversion in <10 minutes | Time 221 OSCEs → 500 patients |
| **Reusability** | Idempotent script | Run twice = same result (no duplicates) |
| **Data Quality** | 0 NULL required fields | All patients have specialty, complexity, presenting_complaint |

### Business Value

- **Time Savings**: 200+ hours manual work → 10 minutes automated
- **Scalability**: Can regenerate patients monthly with new variations
- **Quality**: Consistent Australian medical standards across all patients
- **Student Experience**: Diverse patient pool prevents memorization

---

## A - ARCHITECTURE (How It Will Be Built)

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 OSCE → EMR Converter Pipeline                    │
└─────────────────────────────────────────────────────────────────┘

INPUT: osces table (221 records)
  │
  ├─► STEP 1: NLP Extraction
  │   ├─ Parse patient_instructions (presenting complaint, history)
  │   ├─ Parse vital_signs JSONB (BP, HR, RR, Temp, SpO2)
  │   ├─ Extract specialty from osce_name
  │   ├─ Determine complexity from examiner_checklist length
  │   └─ Output: ClinicalDataDTO
  │
  ├─► STEP 2: Australian Data Generation
  │   ├─ Generate Medicare number (10 digits + Luhn check digit)
  │   ├─ Generate MRN (5-digit hospital number)
  │   ├─ Create Australian names (Aboriginal/TSI culturally appropriate)
  │   ├─ Generate DOB → Calculate age
  │   ├─ Assign indigenous_status (distribution: 3.3% Aboriginal/TSI)
  │   ├─ Generate allergies (10% have drug allergies)
  │   ├─ Generate current_medications (PBS-compliant)
  │   └─ Output: PatientDemographicsDTO
  │
  ├─► STEP 3: Patient Variation
  │   ├─ Create 2-3 variations per OSCE (different ages, genders, backgrounds)
  │   ├─ Same clinical scenario, different patient demographics
  │   ├─ 221 OSCEs × 2.3 avg = 508 patients
  │   └─ Output: List[MockPatientDTO]
  │
  ├─► STEP 4: Database Insertion
  │   ├─ Batch INSERT into mock_patients table
  │   ├─ Link to source OSCE (source_osce_id column)
  │   ├─ Upsert logic (check existing MRN to avoid duplicates)
  │   └─ Output: 500+ patient records
  │
  └─► STEP 5: Validation
      ├─ Verify all Medicare numbers pass Luhn check
      ├─ Verify all required fields populated
      ├─ Check PBS medication codes valid
      ├─ Verify age calculated correctly
      └─ Report: Conversion statistics + errors

OUTPUT: mock_patients table (500+ records)
```

### Component Architecture

```python
# Component 1: NLP Clinical Extractor
class OSCEClinicalExtractor:
    """Extracts clinical data from OSCE text fields"""

    def extract_presenting_complaint(self, osce: OSCE) -> str:
        # Parse patient_instructions for chief complaint
        # Example: "You are a 45-year-old presenting with chest pain"
        pass

    def extract_specialty(self, osce: OSCE) -> str:
        # Cardiology, Neurology, Paediatrics, etc.
        # Map from osce_name keywords
        pass

    def determine_complexity(self, osce: OSCE) -> str:
        # Simple, Moderate, Complex
        # Based on examiner_checklist item count
        pass

    def extract_vital_signs(self, osce: OSCE) -> dict:
        # Parse vital_signs JSONB → standardized format
        pass

# Component 2: Australian Data Generator
class AustralianPatientGenerator:
    """Generates Australian-compliant patient demographics"""

    def generate_medicare_number(self) -> str:
        # 10 digits + Luhn check digit
        # Format: 2345 67890 1 (spaces for readability)
        pass

    def generate_mrn(self) -> str:
        # 5-digit hospital Medical Record Number
        # Prefix: "MRN" + 00001-99999
        pass

    def generate_australian_name(self, indigenous_status: str) -> dict:
        # Culturally appropriate names
        # Aboriginal/TSI: Use respectful name database
        # Non-Indigenous: Common Australian names
        pass

    def generate_indigenous_status(self) -> str:
        # Weighted random (3.3% Aboriginal/TSI)
        # Options: Aboriginal, Torres Strait Islander, Both, Neither
        pass

    def generate_allergies(self) -> list[str]:
        # 10% have drug allergies
        # Australian terminology: penicillin, cephalosporins
        pass

    def generate_pbs_medications(self, age: int, specialty: str) -> dict:
        # Age-appropriate, specialty-relevant medications
        # PBS codes + Australian drug names (paracetamol, salbutamol)
        pass

# Component 3: Batch Converter
class OSCEToEMRConverter:
    """Orchestrates full conversion pipeline"""

    async def convert_all_osces(self) -> ConversionResult:
        osces = await self.fetch_all_osces()
        patients = []

        for osce in osces:
            # Generate 2-3 variations per OSCE
            variations = self.create_patient_variations(osce, count=2)
            patients.extend(variations)

        # Batch insert
        await self.insert_patients(patients)

        # Validate
        validation = await self.validate_patients(patients)

        return ConversionResult(
            total_osces=len(osces),
            total_patients=len(patients),
            validation=validation
        )
```

### Database Schema (from PRD_BACKEND_001)

```sql
-- Target table for generated patients
CREATE TABLE mock_patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mrn VARCHAR(10) UNIQUE NOT NULL,  -- MRN00001-MRN99999
    medicare_number VARCHAR(11),      -- 10 digits + check
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    age_years INTEGER GENERATED ALWAYS AS (
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth))
    ) STORED,
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),
    indigenous_status VARCHAR(100) DEFAULT 'Neither Aboriginal nor Torres Strait Islander',
    allergies TEXT[],                 -- ['Penicillin', 'NSAIDs']
    current_medications JSONB,        -- {drug_name, pbs_code, dose, frequency}
    past_medical_history TEXT[],
    social_history JSONB,             -- {smoking, alcohol, occupation}
    family_history TEXT[],
    vital_signs JSONB,                -- {bp, hr, rr, temp, spo2, gcs}
    presenting_complaint TEXT NOT NULL,
    clinical_scenario TEXT NOT NULL,
    specialty VARCHAR(50) NOT NULL,
    complexity_level VARCHAR(20) NOT NULL CHECK (complexity_level IN ('Simple', 'Moderate', 'Complex')),
    source_osce_id VARCHAR(50) REFERENCES osces(osce_id),  -- Link back to source OSCE
    etg_reference TEXT,               -- eTG guideline URL
    amh_reference TEXT,               -- AMH medication reference
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for quick OSCE lookups
CREATE INDEX idx_mock_patients_source_osce ON mock_patients(source_osce_id);
CREATE INDEX idx_mock_patients_specialty ON mock_patients(specialty);
CREATE INDEX idx_mock_patients_complexity ON mock_patients(complexity_level);
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **NLP Parsing** | Python regex + spaCy (optional) | Extract clinical data from text |
| **Data Generation** | Faker library + custom Australian generators | Demographics, Medicare numbers |
| **Database** | PostgreSQL 15 + SQLAlchemy 2.0 | Insert 500+ patients |
| **Validation** | Pydantic 2.5 | Ensure data quality |
| **CLI** | Typer | Batch conversion script interface |
| **Logging** | Python logging | Track conversion progress |

### Australian Medical Compliance

**Medicare Number Generation** (Critical):
```python
def generate_medicare_number() -> str:
    """
    Australian Medicare number format:
    - 10 digits (2-3-4-1 structure)
    - First digit: 2-6 (state/territory)
    - Luhn check digit (11th digit)

    Example: 2950156481
    """
    state_prefix = random.choice([2, 3, 4, 5, 6])  # NSW, VIC, QLD, SA, WA
    middle_7_digits = random.randint(1000000, 9999999)
    base_10 = f"{state_prefix}{middle_7_digits}"

    # Luhn algorithm for check digit
    check_digit = calculate_luhn_check_digit(base_10)
    return f"{base_10}{check_digit}"

def calculate_luhn_check_digit(number: str) -> int:
    """Calculate Luhn check digit (used by Medicare)"""
    digits = [int(d) for d in number]
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 0:
            doubled = digit * 2
            checksum += doubled if doubled < 10 else doubled - 9
        else:
            checksum += digit
    return (10 - (checksum % 10)) % 10
```

**PBS Medication Mapping**:
```python
PBS_MEDICATIONS = {
    "Cardiology": [
        {"name": "Atorvastatin", "pbs_code": "8251K", "dose": "40mg", "frequency": "Once daily"},
        {"name": "Perindopril", "pbs_code": "8666Q", "dose": "5mg", "frequency": "Once daily"},
        {"name": "Metoprolol", "pbs_code": "2935K", "dose": "50mg", "frequency": "Twice daily"}
    ],
    "Respiratory": [
        {"name": "Salbutamol", "pbs_code": "1945B", "dose": "100mcg", "frequency": "PRN"},
        {"name": "Fluticasone", "pbs_code": "8503C", "dose": "250mcg", "frequency": "Twice daily"}
    ],
    # ... (mapping for all specialties)
}
```

**Indigenous Status Distribution**:
```python
INDIGENOUS_STATUS_WEIGHTS = {
    "Neither Aboriginal nor Torres Strait Islander": 0.967,  # 96.7%
    "Aboriginal but not Torres Strait Islander": 0.025,      # 2.5%
    "Torres Strait Islander but not Aboriginal": 0.003,      # 0.3%
    "Both Aboriginal and Torres Strait Islander": 0.005      # 0.5%
}
```

### Security Considerations

| Risk | Mitigation |
|------|------------|
| **Hardcoded Medicare numbers** | Generate random numbers (not real patient data) |
| **Database credentials** | Use environment variables (from Vault) |
| **Bulk insert performance** | Use batch INSERT with COPY command |
| **Duplicate prevention** | Check existing MRN before insert (UPSERT logic) |
| **Audit trail** | Log conversion timestamp, source OSCE for each patient |

### Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| **Total conversion time** | <10 minutes | 221 OSCEs → 500 patients |
| **Per-patient generation** | <1 second | Clinical extraction + demographics |
| **Database insertion** | <30 seconds | Batch INSERT 500 records |
| **Validation** | <1 minute | Medicare check digit + field validation |

---

## L - LOOP (Iterative Development Plan)

### Development Phases

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Phase 1   │────►│   Phase 2   │────►│   Phase 3   │
│  Foundation │     │     Core    │     │    Polish   │
│   (4-5h)    │     │    (4-5h)   │     │    (2-4h)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
 NLP Extractor      Australian Data     Batch Script
 + Basic Pipeline   Generator + Batch   + Validation
                    Insert              + Documentation
```

### Phase 1: Foundation (4-5 hours)

**Goal**: Build NLP extractor that can parse OSCE text into structured clinical data

**Tasks**:
1. Create `OSCEClinicalExtractor` class
   - Extract presenting complaint from `patient_instructions` (regex patterns)
   - Map `osce_name` → specialty (keyword matching)
   - Parse `vital_signs` JSONB → standardized dict
   - Determine complexity from `examiner_checklist` length

2. Create Pydantic DTOs
   - `ClinicalDataDTO` (extracted from OSCE)
   - `PatientDemographicsDTO` (Australian data)
   - `MockPatientDTO` (final combined model)

3. Write unit tests
   - Test extraction for 10 sample OSCEs
   - Verify specialty mapping accuracy
   - Validate vital signs parsing

**Validation Gate**:
- [ ] Can extract clinical data from 10 OSCEs with 95% accuracy
- [ ] All Pydantic models validate successfully
- [ ] Unit tests pass (≥70% coverage on extractor)

**Deliverables**:
- `backend/src/services/osce_extractor.py` (200 lines)
- `backend/src/schemas/mock_patient.py` (150 lines)
- `backend/tests/test_osce_extractor.py` (100 lines)

---

### Phase 2: Core Functionality (4-5 hours)

**Goal**: Generate Australian-compliant patient demographics and batch insert into database

**Tasks**:
1. Create `AustralianPatientGenerator` class
   - Medicare number generator (10 digits + Luhn check)
   - MRN generator (MRN00001-MRN99999, unique)
   - Australian name generator (culturally appropriate)
   - Indigenous status weighted random
   - Allergy generator (10% have allergies)
   - PBS medication generator (specialty-specific)

2. Create patient variation logic
   - For each OSCE, create 2-3 demographic variations
   - Same clinical scenario, different patient profiles
   - Ensure diversity (age ranges, genders, backgrounds)

3. Implement batch database insertion
   - SQLAlchemy bulk insert (500+ records)
   - UPSERT logic to avoid duplicates
   - Link to source OSCE (`source_osce_id` foreign key)

4. Write integration tests
   - Test full conversion pipeline (10 OSCEs → 23 patients)
   - Verify database constraints (unique MRN, Medicare)
   - Check foreign key integrity

**Validation Gate**:
- [ ] Can generate 100% valid Medicare numbers (Luhn check passes)
- [ ] All PBS medications use Australian drug names
- [ ] Batch insert completes in <30 seconds for 500 records
- [ ] Integration tests pass (100% pass rate)

**Deliverables**:
- `backend/src/services/patient_generator.py` (300 lines)
- `backend/src/services/osce_converter.py` (200 lines)
- `backend/tests/test_patient_generator.py` (150 lines)
- `backend/tests/test_osce_converter_integration.py` (100 lines)

---

### Phase 3: Polish and Validation (2-4 hours)

**Goal**: Create production-ready CLI script with comprehensive validation and error handling

**Tasks**:
1. Create CLI batch conversion script
   - Use Typer for command-line interface
   - Options: `--dry-run`, `--batch-size`, `--force-regenerate`
   - Progress bar (tqdm) for user feedback
   - Detailed logging (conversion stats, errors)

2. Implement comprehensive validation
   - Medicare number Luhn check (100% validation)
   - Required field check (no NULL values)
   - PBS code validation (check against PBS database)
   - Age calculation accuracy
   - Generate validation report (CSV/JSON)

3. Add error handling
   - Graceful failure for malformed OSCE data
   - Rollback on database errors
   - Retry logic for network issues
   - Detailed error messages

4. Write documentation
   - README: How to run batch conversion
   - API documentation (docstrings)
   - Conversion statistics report template

**Validation Gate**:
- [ ] CLI script runs successfully with 0 errors
- [ ] Can convert 221 OSCEs → 500+ patients in <10 minutes
- [ ] Validation report shows 100% Medicare number accuracy
- [ ] Documentation complete (README + docstrings)
- [ ] Manual review of 50 random patients shows clinical accuracy

**Deliverables**:
- `backend/scripts/convert_osces_to_emr_patients.py` (250 lines)
- `backend/src/services/patient_validator.py` (150 lines)
- `backend/scripts/README_OSCE_CONVERTER.md` (100 lines)
- Conversion report: `conversion_stats_2026-02-16.json`

---

## P - PLAN (Detailed Task Breakdown)

### Phase 1 Tasks (Foundation)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **1.1** | Create `backend/src/schemas/mock_patient.py` | 1h | Backend Engineer | PRD_BACKEND_001 (schema knowledge) |
| **1.2** | Implement `OSCEClinicalExtractor.extract_presenting_complaint()` | 1h | Backend Engineer | Access to osces table |
| **1.3** | Implement specialty mapping logic (keywords → specialty) | 0.5h | Backend Engineer | OSCE domain knowledge |
| **1.4** | Implement complexity determination (checklist → Simple/Moderate/Complex) | 0.5h | Backend Engineer | - |
| **1.5** | Parse vital_signs JSONB to standardized format | 1h | Backend Engineer | - |
| **1.6** | Write unit tests for extractor (10 sample OSCEs) | 1h | Backend Engineer | - |
| **1.7** | Validation: Run tests, verify 95% extraction accuracy | 0.5h | Backend Engineer | All above tasks |

**Phase 1 Total**: 5.5 hours

---

### Phase 2 Tasks (Core Functionality)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **2.1** | Implement Medicare number generator with Luhn check | 1h | Backend Engineer | Australian Medicare spec |
| **2.2** | Implement MRN generator (unique 5-digit numbers) | 0.5h | Backend Engineer | - |
| **2.3** | Create Australian name database (including Aboriginal/TSI names) | 1h | Backend Engineer | Cultural sensitivity review |
| **2.4** | Implement indigenous status weighted random | 0.5h | Backend Engineer | ABS statistics (3.3%) |
| **2.5** | Create PBS medication mapping (specialty → medications) | 1.5h | Backend Engineer | PBS database access |
| **2.6** | Implement allergy generator (10% prevalence) | 0.5h | Backend Engineer | - |
| **2.7** | Create patient variation logic (2-3 variations per OSCE) | 1h | Backend Engineer | Phase 1 extractor |
| **2.8** | Implement batch database insert (SQLAlchemy bulk insert) | 1h | Backend Engineer | PRD_BACKEND_001 schema |
| **2.9** | Add UPSERT logic (check existing MRN, avoid duplicates) | 0.5h | Backend Engineer | - |
| **2.10** | Write integration tests (10 OSCEs → 23 patients) | 1h | Backend Engineer | All above tasks |
| **2.11** | Validation: Run integration tests, verify performance | 0.5h | Backend Engineer | - |

**Phase 2 Total**: 9 hours

---

### Phase 3 Tasks (Polish and Validation)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **3.1** | Create CLI script with Typer (command-line interface) | 1h | Backend Engineer | Phase 2 converter |
| **3.2** | Add options: --dry-run, --batch-size, --force-regenerate | 0.5h | Backend Engineer | - |
| **3.3** | Implement progress bar (tqdm) for user feedback | 0.5h | Backend Engineer | - |
| **3.4** | Create patient validator (Medicare Luhn check, required fields) | 1h | Backend Engineer | - |
| **3.5** | Add PBS code validation (check against PBS database) | 0.5h | Backend Engineer | PBS API access |
| **3.6** | Implement error handling (graceful failure, rollback) | 1h | Backend Engineer | - |
| **3.7** | Generate conversion statistics report (JSON/CSV) | 0.5h | Backend Engineer | - |
| **3.8** | Write README documentation (how to run script) | 1h | Backend Engineer | - |
| **3.9** | Add comprehensive docstrings (API documentation) | 0.5h | Backend Engineer | - |
| **3.10** | Manual review: Validate 50 random patients for accuracy | 1h | Backend Engineer + PM | - |
| **3.11** | Final validation: Run full conversion (221 OSCEs → 500 patients) | 0.5h | Backend Engineer | All above tasks |

**Phase 3 Total**: 8 hours

---

### Total Effort Summary

| Phase | Tasks | Effort | Key Deliverable |
|-------|-------|--------|-----------------|
| **Phase 1** | Foundation | 5.5h | NLP extractor working |
| **Phase 2** | Core | 9h | Batch insert 500+ patients |
| **Phase 3** | Polish | 8h | Production CLI script |
| **TOTAL** | - | **22.5h** | 500+ patients ready |

**Note**: Original estimate was 10-14 hours. Revised to 22.5 hours after detailed task breakdown. The increase accounts for:
- Cultural sensitivity (Aboriginal/TSI name database): +1h
- PBS medication mapping (comprehensive): +1.5h
- Manual validation (50 patient review): +1h
- Additional error handling: +1h

---

## H - HANDOFF (Acceptance Criteria and Delivery)

### Acceptance Criteria

#### Functional Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **F1** | OSCE data extraction | 95% accuracy on presenting complaint, specialty, vital signs | Manual review of 50 patients |
| **F2** | Medicare number generation | 100% pass Luhn check digit validation | Automated validation script |
| **F3** | Patient volume | ≥500 unique patients generated from 221 OSCEs | `SELECT COUNT(*) FROM mock_patients` |
| **F4** | Patient variation | 2-3 variations per OSCE (different demographics) | Check patient count / OSCE count ratio |
| **F5** | PBS medication compliance | 100% Australian drug names (no American terms) | Grep for "acetaminophen", "albuterol" (should be 0) |
| **F6** | Indigenous status distribution | ~3.3% Aboriginal/Torres Strait Islander | Query distribution matches ABS statistics |
| **F7** | Batch conversion performance | <10 minutes for full conversion (221 → 500+) | Time CLI script execution |
| **F8** | Idempotency | Running script twice produces same result (no duplicates) | Run conversion twice, verify patient count unchanged |
| **F9** | OSCE linking | All patients have valid `source_osce_id` foreign key | Check foreign key constraint not violated |
| **F10** | Required fields | 0 NULL values in required fields (name, MRN, specialty, etc.) | Query for NULL counts in all required columns |

#### Quality Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **Q1** | Test coverage | ≥70% code coverage | `pytest --cov=src/services` |
| **Q2** | Test pass rate | 100% (zero-tolerance) | `pytest` (all tests must pass) |
| **Q3** | Code quality | 0 linting errors | `ruff check .` |
| **Q4** | Type safety | 0 mypy errors | `mypy src/services/` |
| **Q5** | Documentation | All functions have docstrings | Manual review |

#### Performance Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| **P1** | Total conversion time | <10 minutes | CLI script execution time |
| **P2** | Per-patient generation | <1 second | Time 10 patients, calculate avg |
| **P3** | Database insertion | <30 seconds for 500 records | Batch INSERT timing |
| **P4** | Validation time | <1 minute | Medicare + PBS validation |

#### Security Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **S1** | No hardcoded credentials | 0 instances of database URLs in code | `grep -r "postgresql://" src/` (should be empty) |
| **S2** | Environment variables | All config from env/Vault | Check `os.getenv()` usage |
| **S3** | No real patient data | All Medicare numbers randomly generated | Verify against real Medicare database (should not exist) |
| **S4** | Audit trail | Conversion timestamp logged for all patients | Check `created_at` timestamp consistency |

#### Australian Medical Compliance

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **A1** | Australian drug names | 100% use paracetamol, salbutamol, adrenaline | Grep for American terms (0 occurrences) |
| **A2** | Medicare number format | All follow 10+1 digit format with valid check digit | Luhn validation script |
| **A3** | PBS codes | All medication codes exist in PBS database | Cross-reference PBS API |
| **A4** | Indigenous status | Uses ABS 4-category classification | Check enum values match ABS standard |
| **A5** | SI units | Vital signs in mmol/L, g/L, °C (not mg/dL, °F) | Manual review of 20 patients |
| **A6** | eTG/AMH references | References provided for complex cases | Check `etg_reference` populated for Complex patients |

---

### Testing Requirements

#### Unit Tests

```python
# File: backend/tests/test_osce_extractor.py

class TestOSCEClinicalExtractor:
    """Test OSCE text parsing and clinical data extraction"""

    def test_extract_presenting_complaint(self):
        """Should extract chief complaint from patient_instructions"""
        osce = OSCE(
            patient_instructions="You are a 55-year-old man presenting with chest pain for 2 hours..."
        )
        extractor = OSCEClinicalExtractor()
        complaint = extractor.extract_presenting_complaint(osce)
        assert "chest pain" in complaint.lower()

    def test_specialty_mapping(self):
        """Should map OSCE name keywords to correct specialty"""
        osce = OSCE(osce_name="Cardiology - Acute MI Assessment")
        extractor = OSCEClinicalExtractor()
        specialty = extractor.extract_specialty(osce)
        assert specialty == "Cardiology"

    def test_complexity_determination(self):
        """Should determine complexity from examiner checklist length"""
        osce = OSCE(
            examiner_checklist={
                "items": ["item1", "item2", "item3", "item4", "item5"]  # 5 items = Moderate
            }
        )
        extractor = OSCEClinicalExtractor()
        complexity = extractor.determine_complexity(osce)
        assert complexity == "Moderate"

    def test_vital_signs_parsing(self):
        """Should parse JSONB vital signs to standardized dict"""
        osce = OSCE(
            vital_signs={"BP": "140/90", "HR": "88", "RR": "18", "Temp": "37.2", "SpO2": "98"}
        )
        extractor = OSCEClinicalExtractor()
        vitals = extractor.extract_vital_signs(osce)
        assert vitals["systolic_bp"] == 140
        assert vitals["heart_rate"] == 88
        assert vitals["temperature_celsius"] == 37.2

# File: backend/tests/test_patient_generator.py

class TestAustralianPatientGenerator:
    """Test Australian-compliant data generation"""

    def test_medicare_number_format(self):
        """Should generate 11-digit Medicare number with valid Luhn check"""
        generator = AustralianPatientGenerator()
        medicare = generator.generate_medicare_number()
        assert len(medicare) == 10  # 10 digits (no spaces in storage)
        assert calculate_luhn_check_digit(medicare[:9]) == int(medicare[9])

    def test_mrn_uniqueness(self):
        """Should generate unique MRNs"""
        generator = AustralianPatientGenerator()
        mrns = [generator.generate_mrn() for _ in range(100)]
        assert len(mrns) == len(set(mrns))  # All unique

    def test_indigenous_status_distribution(self):
        """Should match ABS distribution (~3.3% Aboriginal/TSI)"""
        generator = AustralianPatientGenerator()
        statuses = [generator.generate_indigenous_status() for _ in range(10000)]
        aboriginal_pct = sum(1 for s in statuses if "Aboriginal" in s or "Torres Strait" in s) / len(statuses)
        assert 0.025 < aboriginal_pct < 0.045  # ~3.3% with tolerance

    def test_pbs_medications_australian_names(self):
        """Should use Australian drug names (not American)"""
        generator = AustralianPatientGenerator()
        meds = generator.generate_pbs_medications(age=60, specialty="Cardiology")
        american_terms = ["acetaminophen", "albuterol", "epinephrine"]
        for med in meds:
            assert not any(term in med["name"].lower() for term in american_terms)
```

#### Integration Tests

```python
# File: backend/tests/test_osce_converter_integration.py

class TestOSCEConverterIntegration:
    """Test full conversion pipeline"""

    async def test_full_conversion_pipeline(self, db_session):
        """Should convert 10 OSCEs into 23 patients (2.3x variation)"""
        # Arrange: Create 10 sample OSCEs
        osces = await create_sample_osces(count=10)
        converter = OSCEToEMRConverter(db_session)

        # Act: Run conversion
        result = await converter.convert_all_osces()

        # Assert
        assert result.total_osces == 10
        assert 20 <= result.total_patients <= 30  # 2-3 variations per OSCE
        assert result.validation.errors == []

        # Verify database
        patients = await db_session.query(MockPatient).all()
        assert len(patients) == result.total_patients

    async def test_batch_insert_performance(self, db_session):
        """Should insert 500 patients in <30 seconds"""
        patients = [generate_mock_patient() for _ in range(500)]
        converter = OSCEToEMRConverter(db_session)

        start_time = time.time()
        await converter.insert_patients(patients)
        elapsed = time.time() - start_time

        assert elapsed < 30  # Performance target

    async def test_idempotency(self, db_session):
        """Should produce same result when run twice (no duplicates)"""
        converter = OSCEToEMRConverter(db_session)

        # First run
        result1 = await converter.convert_all_osces()
        count1 = await db_session.query(MockPatient).count()

        # Second run (should skip existing)
        result2 = await converter.convert_all_osces()
        count2 = await db_session.query(MockPatient).count()

        assert count1 == count2  # No duplicates
```

#### Manual Validation Checklist

```markdown
# Manual Patient Review Checklist (50 random patients)

For each patient, verify:
- [ ] Full name is culturally appropriate (especially Aboriginal/TSI patients)
- [ ] Medicare number passes online validator
- [ ] MRN is unique and follows format
- [ ] Presenting complaint matches clinical scenario
- [ ] Vital signs are realistic for age/condition
- [ ] Medications are appropriate for specialty
- [ ] PBS codes are valid (cross-reference PBS website)
- [ ] No American terminology (check for acetaminophen, albuterol, etc.)
- [ ] eTG/AMH references are accurate (for Complex cases)
- [ ] Age calculated correctly from DOB

Expected accuracy: ≥95% (47 of 50 patients pass all checks)
```

---

### Documentation Deliverables

#### 1. CLI Script README

**File**: `backend/scripts/README_OSCE_CONVERTER.md`

```markdown
# OSCE to EMR Patient Converter

## Overview
Batch conversion script that transforms 221 existing OSCE scenarios into 500+ mock patient records for EMR practice.

## Prerequisites
- PostgreSQL database with `osces` and `mock_patients` tables
- Python 3.11+ with dependencies installed
- Environment variables: `DATABASE_URL`, `CLAUDE_API_KEY` (optional for validation)

## Usage

### Basic Conversion
```bash
python backend/scripts/convert_osces_to_emr_patients.py
```

### Options
```bash
# Dry run (preview without inserting)
python backend/scripts/convert_osces_to_emr_patients.py --dry-run

# Custom batch size
python backend/scripts/convert_osces_to_emr_patients.py --batch-size 100

# Force regenerate (delete existing, recreate)
python backend/scripts/convert_osces_to_emr_patients.py --force-regenerate

# Verbose logging
python backend/scripts/convert_osces_to_emr_patients.py --verbose
```

## Output
- Console: Progress bar + conversion statistics
- Log file: `conversion_log_YYYY-MM-DD.log`
- Report: `conversion_stats_YYYY-MM-DD.json`

## Validation
After conversion, run validation script:
```bash
python backend/scripts/validate_mock_patients.py
```

Checks:
- Medicare number Luhn check (100% must pass)
- Required fields (0 NULL values)
- PBS code validation
- Australian terminology compliance

## Troubleshooting
- **Error: Duplicate MRN**: Run with `--force-regenerate` to reset
- **Performance slow**: Increase `--batch-size` to 200
- **Foreign key violation**: Ensure all OSCEs exist in database first
```

#### 2. API Documentation (Docstrings)

```python
# File: backend/src/services/patient_generator.py

class AustralianPatientGenerator:
    """
    Generates Australian-compliant patient demographics for EMR practice.

    This service creates realistic patient data following Australian medical standards:
    - Medicare numbers (10 digits + Luhn check digit)
    - MRN (Medical Record Numbers) in hospital format
    - Indigenous status distribution matching ABS statistics (3.3%)
    - PBS-compliant medications with Australian drug names
    - Culturally appropriate names (including Aboriginal/TSI)

    Examples:
        >>> generator = AustralianPatientGenerator()
        >>> medicare = generator.generate_medicare_number()
        >>> print(medicare)
        '2950156481'  # 10 digits, valid Luhn check

        >>> patient = generator.generate_demographics(age=55, specialty="Cardiology")
        >>> print(patient.current_medications)
        [
            {"name": "Atorvastatin", "pbs_code": "8251K", "dose": "40mg"},
            {"name": "Perindopril", "pbs_code": "8666Q", "dose": "5mg"}
        ]

    Attributes:
        name_database (dict): Australian names with cultural metadata
        pbs_medications (dict): PBS medication mapping by specialty
        allergy_database (list): Common drug allergies

    References:
        - Medicare number format: https://www.servicesaustralia.gov.au/
        - PBS medication codes: https://www.pbs.gov.au/
        - ABS Indigenous statistics: https://www.abs.gov.au/
    """

    def generate_medicare_number(self) -> str:
        """
        Generate a valid Australian Medicare number with Luhn check digit.

        Format: 10 digits (state prefix + 7 random digits + Luhn check)
        - First digit: 2-6 (NSW, VIC, QLD, SA, WA)
        - Digits 2-9: Random (7 digits)
        - Digit 10: Luhn check digit

        Returns:
            str: 10-digit Medicare number (no spaces)

        Examples:
            >>> generator = AustralianPatientGenerator()
            >>> medicare = generator.generate_medicare_number()
            >>> len(medicare)
            10
            >>> calculate_luhn_check_digit(medicare[:9]) == int(medicare[9])
            True

        Notes:
            - Generated numbers are random (not real patient data)
            - All numbers pass Luhn validation algorithm
            - State distribution is uniform (20% each state)
        """
        # Implementation here
```

#### 3. Conversion Statistics Report

**File**: `conversion_stats_2026-02-16.json`

```json
{
  "conversion_metadata": {
    "timestamp": "2026-02-16T10:30:45Z",
    "script_version": "1.0.0",
    "total_duration_seconds": 412
  },
  "input_summary": {
    "total_osces": 221,
    "osces_with_valid_data": 221,
    "osces_skipped": 0
  },
  "output_summary": {
    "total_patients_generated": 508,
    "patients_per_osce_avg": 2.3,
    "patients_inserted": 508,
    "patients_updated": 0,
    "patients_failed": 0
  },
  "specialty_distribution": {
    "Cardiology": 68,
    "Neurology": 52,
    "Respiratory": 45,
    "Gastroenterology": 38,
    "Endocrinology": 35,
    "Paediatrics": 62,
    "Psychiatry": 48,
    "Emergency Medicine": 72,
    "Surgery": 45,
    "Other": 43
  },
  "complexity_distribution": {
    "Simple": 127,
    "Moderate": 254,
    "Complex": 127
  },
  "indigenous_status_distribution": {
    "Neither Aboriginal nor Torres Strait Islander": 491,
    "Aboriginal but not Torres Strait Islander": 13,
    "Torres Strait Islander but not Aboriginal": 2,
    "Both Aboriginal and Torres Strait Islander": 2
  },
  "validation_results": {
    "medicare_numbers_valid": 508,
    "medicare_numbers_invalid": 0,
    "pbs_codes_valid": 1243,
    "pbs_codes_invalid": 0,
    "required_fields_complete": 508,
    "required_fields_missing": 0,
    "american_terminology_found": 0
  },
  "performance_metrics": {
    "avg_extraction_time_ms": 450,
    "avg_generation_time_ms": 320,
    "batch_insert_time_seconds": 18,
    "validation_time_seconds": 42
  },
  "errors": []
}
```

---

### Deployment Checklist

**Pre-Deployment**:
- [ ] All unit tests pass (≥70% coverage)
- [ ] All integration tests pass (100% pass rate)
- [ ] Code review approved (Backend Lead)
- [ ] Security scan passed (0 hardcoded credentials)
- [ ] Manual validation completed (50 patients reviewed)

**Deployment Steps**:
1. [ ] Merge PR to `main` branch
2. [ ] Deploy to staging environment
3. [ ] Run conversion script on staging database (dry-run first)
4. [ ] Verify 500+ patients created successfully
5. [ ] Run validation script (Medicare + PBS checks)
6. [ ] Manual spot-check 10 random patients
7. [ ] Deploy to production database
8. [ ] Run production conversion script
9. [ ] Update IMPLEMENTATION_STATUS.md (mark PRD_BACKEND_004 complete)

**Post-Deployment**:
- [ ] Monitor database performance (query times)
- [ ] Verify EMR sessions can assign patients successfully
- [ ] Update documentation with final conversion statistics
- [ ] Archive conversion logs (`conversion_log_*.log`)

---

### Success Validation

**Definition of Done**:

✅ **Functional**:
- 500+ unique mock patients in database
- All patients have valid Medicare numbers (100% Luhn check pass)
- All medications use Australian drug names (0 American terms)
- Patient demographics diverse (age, gender, indigenous status)
- All patients linked to source OSCE

✅ **Quality**:
- Test coverage ≥70%
- Test pass rate 100%
- 0 linting errors
- All functions documented

✅ **Performance**:
- Conversion completes in <10 minutes
- Batch insert in <30 seconds
- Per-patient generation <1 second

✅ **Security**:
- 0 hardcoded credentials
- All config from environment variables
- No real patient data used

✅ **Australian Compliance**:
- Medicare numbers follow Australian format
- PBS codes valid
- Indigenous status distribution matches ABS (3.3%)
- SI units used (°C, mmol/L, not °F, mg/dL)

**Acceptance Sign-Off**:
- [ ] Backend Engineer: Code complete, tests passing
- [ ] PM Coordinator: Requirements met, documentation complete
- [ ] Security Expert: No vulnerabilities found
- [ ] Testing QA: Validation passed (50 patient review)

---

## Related PRDs

**Depends On**:
- PRD_BACKEND_001: EMR Database Migration (needs `mock_patients` table schema)

**Blocks**:
- PRD_BACKEND_002: EMR Session API (needs patient scenarios for session assignment)
- PRD_FRONTEND_001: Epic UI Migration (needs patients to display)
- PRD_FRONTEND_002: Cerner UI Components (needs patients to display)
- All other EMR functionality (requires patient data)

**Integrates With**:
- PRD_INTEGRATION_001: OSCE-EMR Linking (uses `source_osce_id` foreign key)

---

## Appendix: Code Examples

### Full CLI Script Example

```python
# File: backend/scripts/convert_osces_to_emr_patients.py

import asyncio
import typer
from typing import Optional
from tqdm import tqdm
from pathlib import Path
import json
from datetime import datetime

from backend.src.services.osce_extractor import OSCEClinicalExtractor
from backend.src.services.patient_generator import AustralianPatientGenerator
from backend.src.services.osce_converter import OSCEToEMRConverter
from backend.src.services.patient_validator import PatientValidator
from backend.src.database import get_db_session

app = typer.Typer()

@app.command()
def convert(
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without inserting"),
    batch_size: int = typer.Option(100, "--batch-size", help="Batch insert size"),
    force_regenerate: bool = typer.Option(False, "--force-regenerate", help="Delete existing patients"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging")
):
    """
    Convert OSCE scenarios to EMR mock patients.

    Reads all OSCEs from the database, extracts clinical data, generates
    Australian-compliant patient demographics, and inserts into mock_patients table.

    Examples:
        # Standard conversion
        python convert_osces_to_emr_patients.py

        # Preview without inserting
        python convert_osces_to_emr_patients.py --dry-run

        # Force regenerate all patients
        python convert_osces_to_emr_patients.py --force-regenerate
    """
    asyncio.run(async_convert(dry_run, batch_size, force_regenerate, verbose))

async def async_convert(dry_run: bool, batch_size: int, force_regenerate: bool, verbose: bool):
    """Async conversion logic"""

    # Setup logging
    log_file = Path(f"conversion_log_{datetime.now().strftime('%Y-%m-%d')}.log")
    logger = setup_logger(log_file, verbose)

    logger.info("Starting OSCE → EMR patient conversion")

    # Database session
    async with get_db_session() as db:
        converter = OSCEToEMRConverter(db, batch_size=batch_size)

        # Force regenerate: delete existing patients
        if force_regenerate:
            logger.warning("Force regenerate: Deleting existing mock patients")
            if not dry_run:
                await db.execute("DELETE FROM mock_patients")
                await db.commit()

        # Fetch OSCEs
        logger.info("Fetching OSCEs from database")
        osces = await converter.fetch_all_osces()
        logger.info(f"Found {len(osces)} OSCEs")

        # Convert with progress bar
        patients = []
        with tqdm(total=len(osces), desc="Converting OSCEs") as pbar:
            for osce in osces:
                try:
                    # Generate 2-3 variations per OSCE
                    variations = converter.create_patient_variations(osce, count=2)
                    patients.extend(variations)
                    pbar.update(1)
                except Exception as e:
                    logger.error(f"Failed to convert OSCE {osce.osce_id}: {e}")

        logger.info(f"Generated {len(patients)} patients from {len(osces)} OSCEs")

        # Insert patients (unless dry-run)
        if not dry_run:
            logger.info("Inserting patients into database")
            await converter.insert_patients(patients)
            logger.info("Patients inserted successfully")
        else:
            logger.info("Dry-run mode: Skipping database insertion")

        # Validate patients
        logger.info("Validating patient data")
        validator = PatientValidator()
        validation_result = validator.validate_all(patients)

        # Generate statistics report
        stats = generate_conversion_stats(osces, patients, validation_result)
        stats_file = Path(f"conversion_stats_{datetime.now().strftime('%Y-%m-%d')}.json")
        stats_file.write_text(json.dumps(stats, indent=2))
        logger.info(f"Statistics saved to {stats_file}")

        # Print summary
        print("\n" + "="*60)
        print("CONVERSION SUMMARY")
        print("="*60)
        print(f"OSCEs processed: {len(osces)}")
        print(f"Patients generated: {len(patients)}")
        print(f"Medicare validation: {validation_result['medicare_valid']}/{len(patients)}")
        print(f"PBS validation: {validation_result['pbs_valid']}/{validation_result['pbs_total']}")
        print(f"Errors: {len(validation_result['errors'])}")
        print("="*60)

if __name__ == "__main__":
    app()
```

### Medicare Number Generator

```python
# File: backend/src/services/patient_generator.py

import random
from typing import List

def calculate_luhn_check_digit(number: str) -> int:
    """
    Calculate Luhn check digit (used by Medicare, credit cards).

    Algorithm:
    1. Reverse the digits
    2. Double every second digit
    3. If doubled digit > 9, subtract 9
    4. Sum all digits
    5. Check digit = (10 - (sum % 10)) % 10

    Args:
        number: String of digits (without check digit)

    Returns:
        Check digit (0-9)

    Examples:
        >>> calculate_luhn_check_digit("295015648")
        1
        >>> calculate_luhn_check_digit("234567890")
        7
    """
    digits = [int(d) for d in number]
    checksum = 0

    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 0:  # Every second digit (0-indexed)
            doubled = digit * 2
            checksum += doubled if doubled < 10 else doubled - 9
        else:
            checksum += digit

    return (10 - (checksum % 10)) % 10

class AustralianPatientGenerator:
    """Generate Australian-compliant patient demographics"""

    STATE_PREFIXES = [2, 3, 4, 5, 6]  # NSW, VIC, QLD, SA, WA

    def generate_medicare_number(self) -> str:
        """
        Generate valid Australian Medicare number.

        Format: [state][7-digits][check]
        Example: 2950156481

        Returns:
            10-digit Medicare number (no spaces)
        """
        state_prefix = random.choice(self.STATE_PREFIXES)
        middle_7_digits = random.randint(1000000, 9999999)
        base_9 = f"{state_prefix}{middle_7_digits}"
        check_digit = calculate_luhn_check_digit(base_9)

        return f"{base_9}{check_digit}"

    def generate_mrn(self) -> str:
        """
        Generate Medical Record Number.

        Format: MRN + 5 digits (MRN00001-MRN99999)

        Returns:
            Unique MRN string
        """
        number = random.randint(1, 99999)
        return f"MRN{number:05d}"

    def generate_pbs_medications(self, age: int, specialty: str) -> List[dict]:
        """
        Generate PBS-compliant medications for patient.

        Uses Australian drug names (paracetamol, salbutamol, adrenaline).
        Filters by age appropriateness and specialty relevance.

        Args:
            age: Patient age (years)
            specialty: Medical specialty (Cardiology, Respiratory, etc.)

        Returns:
            List of medications with PBS codes

        Examples:
            >>> generator = AustralianPatientGenerator()
            >>> meds = generator.generate_pbs_medications(60, "Cardiology")
            >>> meds[0]
            {
                "name": "Atorvastatin",
                "pbs_code": "8251K",
                "dose": "40mg",
                "frequency": "Once daily",
                "indication": "Hypercholesterolaemia"
            }
        """
        PBS_DATABASE = {
            "Cardiology": [
                {"name": "Atorvastatin", "pbs_code": "8251K", "dose": "40mg", "frequency": "Once daily"},
                {"name": "Perindopril", "pbs_code": "8666Q", "dose": "5mg", "frequency": "Once daily"},
                {"name": "Metoprolol", "pbs_code": "2935K", "dose": "50mg", "frequency": "Twice daily"},
                {"name": "Aspirin", "pbs_code": "1234A", "dose": "100mg", "frequency": "Once daily"},
            ],
            "Respiratory": [
                {"name": "Salbutamol", "pbs_code": "1945B", "dose": "100mcg", "frequency": "PRN"},
                {"name": "Fluticasone", "pbs_code": "8503C", "dose": "250mcg", "frequency": "Twice daily"},
                {"name": "Montelukast", "pbs_code": "8723M", "dose": "10mg", "frequency": "Once daily at night"},
            ],
            # ... (full PBS mapping)
        }

        # Get specialty-specific medications
        specialty_meds = PBS_DATABASE.get(specialty, [])

        # Filter by age appropriateness (example: no aspirin for children)
        if age < 18:
            specialty_meds = [m for m in specialty_meds if m["name"] != "Aspirin"]

        # Return 2-4 random medications
        count = random.randint(2, min(4, len(specialty_meds)))
        return random.sample(specialty_meds, count)
```

---

**End of PRD_BACKEND_004**

**Next Steps**: After this PRD is approved, move to frontend PRDs (PRD_FRONTEND_001: Epic UI Migration).

**Total Backend PRDs**: 4 of 4 complete (100%)
**Total Project PRDs**: 4 of 14 complete (29%)
