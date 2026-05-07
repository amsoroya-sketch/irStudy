# 13-Gate Medical Content Quality Checklist

**Reference Document** - Loaded on demand for detailed quality gate requirements

**Source**: Based on Batch 1 clinical content validation (207 personas, 96.5% deployment readiness)

---

## Gate 1: JSON Compliance

**Requirement**: All 17 required fields present and correctly formatted

**Required Fields**:
1. `persona_id` (string)
2. `persona_name` (string)
3. `age` (integer)
4. `gender` (string: "Male", "Female", "Non-binary")
5. `background` (object with cultural/social details)
6. `presenting_complaint` (string)
7. `history_of_presenting_complaint` (array of structured elements)
8. `past_medical_history` (array)
9. `medications` (array with dosing, frequency)
10. `allergies` (array or "NKDA")
11. `social_history` (object)
12. `family_history` (object)
13. `examination_findings` (object with vital signs + systems)
14. `differential_diagnosis` (array with probabilities)
15. `management_plan` (array)
16. `educational_learning_points` (array)
17. `rag_citations` (array of exactly 3 citations)

**Validation Command**:
```python
python scripts/validate_json_structure.py --check-all-fields data/osce/persona_001.json
```

---

## Gate 2: RAG Citation Quality

**Requirement**:
- Exactly 3 citations per OSCE case
- Each citation must have `qdrant_point_id`
- Confidence score ≥0.65 (production: ≥0.70)
- Page numbers when applicable
- Zero hallucinated citations (verified against Qdrant DB)

**Example Valid Citation**:
```json
{
  "qdrant_point_id": "abc123-def456-...",
  "source": "eTG Complete - Cardiovascular",
  "relevant_quote": "Acute chest pain requires immediate ECG...",
  "page": 245,
  "confidence_score": 0.82
}
```

**Validation Command**:
```python
python scripts/validate_rag_citations.py --min-confidence 0.65 --check-qdrant data/osce/
```

---

## Gate 3: FRACP Clinical Validation

**Requirement**: FRACP reviewer score ≥8.0/10

**Review Criteria**:
- Clinical accuracy (diagnosis, management)
- Appropriateness for level (intern/resident/registrar)
- Educational value
- Realism of presentation
- Safety (no dangerous errors)

**Current Performance**: 8.3/10 average (Batch 1)

**Validation Command**:
```python
python scripts/fracp_review_validation.py data/osce/batch_1/
```

---

## Gate 4: Clinical Accuracy

**Medication Safety**:
- ✅ Correct generic names (Australian)
- ✅ Appropriate dosing (adult/pediatric)
- ✅ Correct route of administration
- ✅ No contraindicated combinations

**Diagnostic Accuracy**:
- ✅ Differentials ranked by probability
- ✅ Red flags identified
- ✅ Appropriate investigations ordered

**Example (WRONG)**:
```json
"medications": [
  {"name": "acetaminophen", "dose": "500mg", "frequency": "PRN"}  // ❌ US name
]
```

**Example (CORRECT)**:
```json
"medications": [
  {"name": "paracetamol", "dose": "1g", "frequency": "QID", "route": "PO"}  // ✅
]
```

---

## Gate 5: Australian Medical Context

**Requirements**:
- ✅ Australian drug names (paracetamol, salbutamol, adrenaline)
- ✅ MBS item numbers where applicable
- ✅ PBS listings for medications
- ✅ Australian clinical guidelines (eTG, RACGP, Therapeutic Guidelines)
- ✅ AHPRA registration context

**Target**: ≥60% Australian sources in RAG citations
**Current**: 66.1% (Batch 1) ✅

**Validation Command**:
```bash
grep -r "acetaminophen\|albuterol\|epinephrine" data/ --include="*.json"
# Expected output: No matches
```

---

## Gates 6-7: Difficulty & Specialty

**Difficulty Levels**:
- `basic`: Medical student / intern
- `intermediate`: Resident / PGY2-3
- `advanced`: Registrar / specialty training

**Specialties** (valid values):
- General Medicine, Cardiology, Respiratory, Gastroenterology
- Neurology, Endocrinology, Rheumatology, Infectious Diseases
- Emergency Medicine, General Practice, Pediatrics, etc.

**Validation**: Must match case complexity to assigned level

---

## Gates 8-10: Cultural Safety

### Gate 8: Aboriginal and Torres Strait Islander

**Requirements**:
- Culturally appropriate terminology
- Recognition of health disparities
- Access to Aboriginal Health Services
- Traditional medicine respect

**Example**:
```json
"background": {
  "cultural_identity": "Aboriginal Australian (Wiradjuri Nation)",
  "community_connections": "Strong ties to local Aboriginal Health Service",
  "cultural_considerations": "Prefers involvement of Aboriginal Health Worker in consultations"
}
```

### Gate 9: LGBTQIA+ Inclusivity

**Requirements**:
- Inclusive language
- Preferred pronouns respected
- Same-sex partner recognition
- Gender-affirming care when relevant

**Example**:
```json
"gender": "Non-binary",
"pronouns": "they/them",
"social_history": {
  "partner": "Lives with partner (they/them) of 5 years"
}
```

### Gate 10: CALD (Culturally and Linguistically Diverse)

**Requirements**:
- Interpreter services when needed
- Cultural health beliefs respected
- Language barriers addressed
- Family involvement patterns

**Example**:
```json
"background": {
  "country_of_origin": "Vietnam",
  "languages": ["Vietnamese (primary)", "English (conversational)"],
  "interpreter_required": true,
  "cultural_health_beliefs": "Prefers traditional Vietnamese medicine alongside Western treatment"
}
```

---

## Gates 11-12: Security

### Gate 11: Zero Credentials

**Check**: No API keys, passwords, tokens in content

**Validation Command**:
```bash
grep -r "API_KEY\|password\|token\|secret" data/ --include="*.json"
# Expected: 0 matches
```

### Gate 12: Zero PHI (Protected Health Information)

**Requirements**:
- No real patient names (use synthetic names)
- No real MRNs (use synthetic IDs)
- No real addresses (use generic "suburban Melbourne")
- No real phone numbers
- Hash any identifiers in logs

**Example (SAFE)**:
```json
"persona_name": "Sarah Chen",  // ✅ Synthetic name
"mrn": "MRN-SYN-001234",       // ✅ Clearly synthetic
"address": "Suburban Brisbane"  // ✅ Generic location
```

---

## Gate 13: Educational Alignment

**9-Step Clinical History Framework**:
1. Presenting complaint
2. History of presenting complaint (SOCRATES for pain)
3. Past medical history
4. Medications (including dose, frequency, adherence)
5. Allergies
6. Social history (ETOH, smoking, occupation, living situation)
7. Family history
8. Systems review
9. ICE (Ideas, Concerns, Expectations)

**Red Flags Identification**:
- Chest pain: MI, PE, aortic dissection
- Headache: SAH, meningitis, raised ICP
- Abdominal pain: AAA, ectopic, perforation

**Validation**: All OSCE cases must follow 9-step structure

---

## Summary: Gate Pass Rates (Batch 1 - 207 Personas)

| Gate | Requirement | Pass Rate |
|------|-------------|-----------|
| 1. JSON Compliance | 17 fields valid | 100% ✅ |
| 2. RAG Citations | ≥0.65 confidence, 3 citations | 100% ✅ |
| 3. FRACP Review | ≥8.0/10 | 100% ✅ (avg 8.3) |
| 4. Clinical Accuracy | No dangerous errors | 100% ✅ |
| 5. Australian Context | ≥60% AU sources | 100% ✅ (66.1%) |
| 6-7. Difficulty/Specialty | Valid mapping | 100% ✅ |
| 8-10. Cultural Safety | Inclusive content | 100% ✅ |
| 11-12. Security | Zero credentials/PHI | 100% ✅ |
| 13. Educational | 9-step history | 100% ✅ |
| **OVERALL** | **All gates pass** | **96.5% deployment ready** |

**Notes**:
- 7 personas (3.5%) required minor FRACP review adjustments
- Zero hallucinated citations across 3,726 total citations
- Zero US drug name violations after initial cleanup
- 100% UTF-8 encoding compliance
