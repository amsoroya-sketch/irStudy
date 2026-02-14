# Medical Accuracy Standards

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Medical Accuracy Standards

### 1.1 Australian Medical Context (MANDATORY)

**ALWAYS use Australian standards and resources:**

- **Primary Sources**:
  - Therapeutic Guidelines (eTG) - Australian treatment guidelines
  - PBS (Pharmaceutical Benefits Scheme) - Australian drug listings
  - AHPRA - Australian Health Practitioner Regulation Agency standards
  - NSW Health guidelines - Local health district protocols
  - AMC (Australian Medical Council) - Exam standards
  - AMH (Australian Medicines Handbook)

**NEVER use:**
- American drug names without Australian equivalents
- Non-Australian treatment protocols without qualification
- Non-AHPRA standards
- UpToDate without Australian context

### 1.2 Australian Spelling & Terminology (MANDATORY)

**CORRECT Australian Spelling:**
```
paediatric (NOT pediatric)
anaesthesia (NOT anesthesia)
oesophagus (NOT esophagus)
haemoglobin (NOT hemoglobin)
anaemia (NOT anemia)
paracetamol (NOT acetaminophen - different drug name!)
adrenaline (NOT epinephrine)
salbutamol (NOT albuterol)
colour (NOT color)
oestrogen (NOT estrogen)
```

**Australian Medical Terms:**
```
GP (NOT PCP or primary care physician)
Emergency Department (NOT ER or emergency room)
Specialist (NOT attending)
Referral (NOT consult)
Bulk-billed (NOT covered by insurance)
Medicare (NOT insurance)
```

**Example - CORRECT:**
```python
drug_info = {
    'name': 'paracetamol',  # Australian name
    'indication': 'Management of paediatric fever',
    'dose': '15 mg/kg',
    'max_dose': '60 mg/kg/day',
    'source': 'Therapeutic Guidelines: Paediatric, Section 2.1'
}
```

**Example - INCORRECT:**
```python
drug_info = {
    'name': 'acetaminophen',  # ❌ American name
    'indication': 'Management of pediatric fever',  # ❌ American spelling
    'source': 'UpToDate'  # ❌ American source without context
}
```

### 1.3 Clinical Accuracy Requirements

**Drug Dosages:**
- ALWAYS include units (mg, mcg, mL, units/kg)
- ALWAYS specify age/weight ranges
- ALWAYS cite Therapeutic Guidelines or PBS
- ALWAYS note PBS restrictions if applicable

**Example - CORRECT:**
```python
dosage = {
    'drug': 'amoxicillin',
    'dose': '500 mg',
    'frequency': 'three times daily (TDS)',
    'duration': '5-7 days',
    'indication': 'Community-acquired pneumonia',
    'citation': 'Therapeutic Guidelines: Antibiotic, Section 2.3.1 (2024)',
    'pbs_listed': True,
    'restrictions': 'None'
}
```

**Red Flags:**
- ALWAYS flag life-threatening conditions
- ALWAYS recommend immediate referral for emergencies
- ALWAYS include safety warnings
- ALWAYS use "000" for emergency calls (Australian emergency number)

**Example - CORRECT:**
```python
if symptoms_include(['chest_pain', 'radiation_to_arm', 'diaphoresis']):
    return {
        'red_flag': True,
        'severity': 'CRITICAL',
        'action': 'Call ambulance (000) immediately - suspect acute coronary syndrome',
        'immediate_management': 'Aspirin 300mg PO, oxygen if hypoxic, IV access',
        'citation': 'NSW Health: Acute Coronary Syndrome Protocol (2024)'
    }
```

**SI Units (Australian Standard):**
```python
# ✅ CORRECT - SI units
glucose = {'value': 5.5, 'unit': 'mmol/L'}
sodium = {'value': 140, 'unit': 'mmol/L'}

# ❌ INCORRECT - American units
glucose = {'value': 100, 'unit': 'mg/dL'}  # Don't use mg/dL
```

### 1.4 Citation Requirements (MANDATORY)

**EVERY medical claim MUST have exact reference with page/section numbers:**

#### Citation Format Requirements

**✅ REQUIRED - Book citations MUST include page numbers:**
```markdown
✅ (Talley & O'Connor's Clinical Examination, 8th ed, p.145)
✅ (Murtagh's General Practice, 8th ed, p.892)
✅ (Oxford Handbook of Emergency Medicine, 5th ed, p.234)
✅ (AMC Clinical Exam Handbook, p.67)

❌ (Talley & O'Connor's Clinical Examination, 8th ed)  # Missing page number
❌ (Murtagh's General Practice, 8th ed)  # Missing page number
```

**✅ REQUIRED - eTG citations MUST include section numbers:**
```markdown
✅ (Therapeutic Guidelines: Paediatric, Section 2.3.1, 2024)
✅ (Therapeutic Guidelines: Surgery, Section 1.4.2, 2024)
✅ (Therapeutic Guidelines: Cardiovascular, Section 5.2, 2024)

❌ (Therapeutic Guidelines: Paediatric, 2024)  # Missing section number
❌ (eTG Paediatric, 2024)  # Missing section number
```

**✅ REQUIRED - RAG verification for auto-citations:**
- Minimum confidence threshold: **>0.65** for automatic page/section addition
- All auto-generated citations MUST be RAG-verified against actual medical textbooks
- RAG collection: `medical_knowledge` (9,672+ medical text chunks)
- Embedding model: `pritamdeka/S-PubMedBert-MS-MARCO`

**❌ NEVER use generic citations:**
```markdown
❌ (eTG 2024)  # No specialty, no section
❌ (Talley)  # No edition, no page
❌ (Australian guidelines)  # Too vague
❌ (Standard practice)  # Not a citation
```

#### RAG-Verified Citation Workflow

```python
# ✅ CORRECT - RAG-verified citation with exact page
question = {
    'stem': 'What is the first-line antibiotic for community-acquired pneumonia?',
    'answer': 'Amoxicillin 1g TDS for 5 days',
    'explanation': 'Amoxicillin is first-line for CAP in previously well patients.',
    'citation': '(Therapeutic Guidelines: Antibiotic, Section 2.3.1, 2024)',
    'rag_confidence': 0.87,
    'rag_verified': True
}

# ❌ INCORRECT - Generic citation without section
question = {
    'stem': 'What is the first-line antibiotic for community-acquired pneumonia?',
    'answer': 'Amoxicillin 1g TDS for 5 days',
    'explanation': 'Amoxicillin is first-line for CAP.',
    'citation': '(Therapeutic Guidelines: Antibiotic, 2024)',  # ❌ Missing section
    'rag_verified': False
}
```

#### RAG Metadata Validation (Week 2 Phase 3 Enhancement)

**MANDATORY: All RAG citations MUST have complete metadata**

**CONTEXT**: Week 1 mistake had 212/212 citations with `title: "Unknown"` due to missing RAG database metadata. Phase 3 prevention system validates metadata BEFORE content generation.

**Required Metadata Fields (ZERO TOLERANCE):**

| Field | Requirement | Valid | Invalid |
|-------|-------------|-------|---------|
| `title` | NOT "Unknown", not empty | "John Murtagh General Practice" | "Unknown", "" |
| `author` | NOT "Unknown" (preferred) | "John Murtagh" | "" (empty) |
| `year` | 1990-2026 range | "2020", "2023" | "Unknown", <1990 |
| `page` | >0 | 42, 1234 | 0, -1, "N/A" |

**NOTE**: `author: "Unknown Author"` is acceptable for 16% of books with generic filenames.

**Pre-Flight Validation (MANDATORY before generation):**

```bash
# MUST run before ANY MCQ/OSCE generation
./scripts/pre_flight_validation.sh

# EXIT CODE 0 = Safe to proceed
# EXIT CODE 1 = DO NOT PROCEED (fix issues first)
```

**Incremental Validation (fail-fast in generation):**

```python
from src.agents.qa.incremental_citation_validator import validate_citation_immediate

# In generation loop - validate IMMEDIATELY after RAG retrieval
for i in range(num_mcqs):
    # ... RAG retrieval ...
    citations = rag_search(query)

    # CRITICAL: Validate immediately (fail-fast)
    try:
        validate_citation_immediate(
            citations=citations,
            question_id=f"MCQ-{i+1:03d}",
            fail_fast=True  # Raise exception on first invalid citation
        )
    except CitationValidationError as e:
        # STOP generation immediately
        logger.error(f"Citation validation failed: {e}")
        raise

    # Only reach here if validation passed
    mcq = create_mcq(question_data, citations)
```

**See [RAG Citation Requirements](11-rag-citation-requirements.md) for complete validation documentation.**

#### Acceptable Citation Sources (with exact references)

**Primary Australian Sources:**
- **Therapeutic Guidelines (eTG)**: MUST include Section X.Y.Z
  - Example: `(Therapeutic Guidelines: Paediatric, Section 2.3.1, 2024)`
- **Talley & O'Connor's Clinical Examination**: MUST include page number
  - Example: `(Talley & O'Connor's Clinical Examination, 8th ed, p.145)`
- **Murtagh's General Practice**: MUST include page number
  - Example: `(Murtagh's General Practice, 8th ed, p.892)`
- **AMC Handbook of Clinical Assessment**: MUST include page number
  - Example: `(AMC Handbook of Clinical Assessment, p.67)`
- **Oxford Handbook of Emergency Medicine**: MUST include page number
  - Example: `(Oxford Handbook of Emergency Medicine, 5th ed, p.234)`

**Secondary Sources (when primary not available):**
- NSW Health Clinical Practice Guidelines (with document title and section)
- RACGP Guidelines (with section/page)
- Australian Medicines Handbook (with page)

#### Exceptions

**ONLY exception - General knowledge statements:**
- Statements about AMC exam structure (e.g., "AMC exam has 16 stations")
- Basic anatomy facts universally accepted
- General medical definitions

**All clinical claims, drug dosages, treatment protocols, diagnostic criteria MUST have exact citations with page/section numbers.**

#### Validation

Use `validate_exact_citations.py` to ensure:
- [ ] All citations have page numbers (books) OR section numbers (eTG)
- [ ] No generic citations remain
- [ ] RAG confidence scores logged for all auto-citations
- [ ] Manual review completed for low-confidence matches (<0.65)

---

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
