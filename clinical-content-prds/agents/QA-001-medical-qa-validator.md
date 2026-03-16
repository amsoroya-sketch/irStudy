# QA-001: Medical QA Validator Agent

**Agent ID**: QA-001
**Agent Name**: medical-qa-validator
**Role**: Quality Assurance Validator (NOT a persona creator)
**Reviews**: ALL 360 personas across all 12 medical specialties
**Quality Gates**: JSON compliance, RAG citations, clinical accuracy, cultural safety, security
**Output**: QA report JSON with pass/fail recommendations and deployment readiness score
**Batch**: Final Validation (runs AFTER all MED-001 through MED-012 complete)

---

## Role Definition

**QA-001 does NOT create personas**. It VALIDATES personas created by MED-001 through MED-012.

**Validation Scope**:
- Technical compliance: JSON format, RAG citations, required fields
- Clinical accuracy: Diagnosis correct, management appropriate, no dangerous advice
- Cultural safety: No stereotypes, cultural liaison review complete
- Educational quality: Difficulty appropriate, AMC alignment, learning objectives
- Security: No hardcoded credentials, PHI protected

---

## Validation Domains (5 Categories)

### 1. Technical Compliance

**JSON Template Validation**:
```python
def validate_json_compliance(persona_json):
    errors = []

    # Required fields (all 360 personas)
    required_fields = [
        "id", "name", "age", "gender", "specialty", "difficulty",
        "chief_complaint", "symptoms", "opening_statement", "emotional_baseline",
        "past_medical_history", "medications", "allergies",
        "family_history", "social_history",
        "expected_diagnosis", "expected_management", "critical_errors"
    ]

    for field in required_fields:
        if field not in persona_json:
            errors.append(f"Missing required field: {field}")

    return errors
```

**RAG Citation Validation**:
```python
def validate_rag_citations(persona_json):
    errors = []

    for symptom in persona_json.get("symptoms", []):
        # Check 1: RAG citation exists
        if "rag_citation" not in symptom:
            errors.append(f"Symptom '{symptom['symptom']}' missing RAG citation")
            continue

        # Check 2: Confidence >0.65
        citation = symptom["rag_citation"]
        if citation.get("confidence", 0) < 0.65:
            errors.append(f"RAG citation confidence {citation['confidence']} < 0.65 threshold")

        # Check 3: Source specified
        if not citation.get("source"):
            errors.append(f"RAG citation missing source")

        # Check 4: Quote provided
        if not citation.get("quote"):
            errors.append(f"RAG citation missing quote")

    return errors
```

**FRACP Review Validation**:
```python
def validate_fracp_reviews(persona_json):
    errors = []

    reviews = persona_json.get("fracp_reviews", []) or persona_json.get("clinical_educator_reviews", [])

    # Check 1: At least 2 reviews
    if len(reviews) < 2:
        errors.append(f"Only {len(reviews)} reviews found (minimum 2 required)")

    # Check 2: All reviews approved
    for review in reviews:
        if not review.get("approved"):
            errors.append(f"Review by {review.get('reviewer_name')} not approved")

    return errors
```

---

### 2. Clinical Accuracy

**Critical Error Detection**:
```python
def validate_clinical_accuracy(persona_json):
    errors = []

    # Check 1: Diagnosis matches symptoms
    diagnosis = persona_json.get("expected_diagnosis", "").lower()
    symptoms_str = str(persona_json.get("symptoms", [])).lower()

    # Example: STEMI should have chest pain
    if "stemi" in diagnosis and "chest pain" not in symptoms_str:
        errors.append("STEMI diagnosis but no chest pain in symptoms")

    # Check 2: Dangerous advice not present
    management_str = str(persona_json.get("expected_management", [])).lower()
    dangerous_patterns = [
        ("nsaid" in management_str and "acute kidney injury" in str(persona_json)),
        ("aspirin" in management_str and "active peptic ulcer" in str(persona_json)),
        ("warfarin" in management_str and "pregnant" in str(persona_json))
    ]

    if any(dangerous_patterns):
        errors.append("Dangerous medication advice detected (contraindicated)")

    # Check 3: Critical errors defined
    if not persona_json.get("critical_errors"):
        errors.append("No critical errors defined (required for auto-fail logic)")

    return errors
```

---

### 3. Cultural Safety

**Stereotype Detection**:
```python
def validate_cultural_safety(persona_json):
    errors = []

    cultural_bg = persona_json.get("cultural_background", "").lower()

    # Aboriginal/TSI personas
    if "aboriginal" in cultural_bg or "torres strait" in cultural_bg:
        # Check for stereotypes
        stereotype_phrases = ["non-compliant", "alcohol abuse", "unemployed", "poor english"]
        persona_str = str(persona_json).lower()

        for phrase in stereotype_phrases:
            if phrase in persona_str and "anti_stereotyping" not in persona_str:
                errors.append(f"Potential stereotype detected: '{phrase}' in Aboriginal/TSI persona")

        # Check Nation specified
        nations = ["noongar", "wurundjeri", "eora", "kaurna", "palawa", "yolngu"]
        if not any(nation in persona_str for nation in nations):
            errors.append("Aboriginal/TSI persona missing Nation specification")

        # Check cultural liaison review
        if "cultural_liaison_review" not in persona_json:
            errors.append("Aboriginal/TSI persona missing cultural liaison review (MANDATORY)")

    # LGBTQIA+ personas
    if "transgender" in cultural_bg or "lgbtq" in cultural_bg:
        # Check pronouns consistent
        if "pronouns" not in persona_json:
            errors.append("LGBTQIA+ persona missing pronouns specification")

        # Check educator review
        if "lgbtqia_educator_review" not in persona_json and "lgbtqia+" in str(persona_json).lower():
            errors.append("LGBTQIA+ persona missing educator review (MANDATORY)")

    return errors
```

---

### 4. Educational Quality

**Difficulty Validation**:
```python
def validate_educational_quality(persona_json):
    errors = []

    difficulty = persona_json.get("difficulty")

    # Check 1: Difficulty specified
    if difficulty not in ["Easy", "Medium", "Hard"]:
        errors.append(f"Invalid difficulty: {difficulty} (must be Easy, Medium, or Hard)")

    # Check 2: Complexity matches difficulty
    symptoms_count = len(persona_json.get("symptoms", []))
    comorbidities_count = len(persona_json.get("past_medical_history", []))

    if difficulty == "Easy" and (symptoms_count > 5 or comorbidities_count > 2):
        errors.append("Easy difficulty but complex presentation (too many symptoms/comorbidities)")

    if difficulty == "Hard" and (symptoms_count < 8 or comorbidities_count < 3):
        errors.append("Hard difficulty but simple presentation (add complexity)")

    return errors
```

---

### 5. Security

**Credential Detection**:
```python
def validate_security(persona_json):
    errors = []

    persona_str = str(persona_json)

    # Check 1: No API keys
    if "api_key" in persona_str.lower() or "secret_key" in persona_str.lower():
        errors.append("SECURITY VIOLATION: API key detected in persona JSON")

    # Check 2: No database credentials
    if "db_password" in persona_str.lower() or "dbKey" in persona_str:
        errors.append("SECURITY VIOLATION: Database credentials in persona JSON")

    # Check 3: No file paths
    if "/home/" in persona_str or "C:\\" in persona_str:
        errors.append("SECURITY VIOLATION: File paths in persona JSON")

    return errors
```

---

## QA Report Output Format

**Comprehensive QA Report** (JSON):

```json
{
  "qa_report_version": "1.0",
  "validation_date": "2026-03-25",
  "total_personas_reviewed": 360,
  "total_personas_passed": 352,
  "total_personas_failed": 8,
  "pass_rate": "97.8%",

  "quality_metrics": {
    "avg_rag_citation_confidence": 0.74,
    "avg_fracp_reviews_per_persona": 2.2,
    "avg_clinical_accuracy_score": 9.3,
    "cultural_safety_score": 9.7
  },

  "distribution_validation": {
    "difficulty": {
      "easy": 125,
      "medium": 148,
      "hard": 87,
      "target_easy": 125,
      "target_medium": 148,
      "target_hard": 87,
      "status": "PASS (matches target distribution)"
    },
    "specialty": {
      "cardiology": 45,
      "emergency": 45,
      "general_practice": 54,
      "pediatrics": 36,
      "respiratory": 36,
      "neurology": 27,
      "obgyn": 27,
      "surgery": 27,
      "psychiatry": 36,
      "infectious_diseases": 27,
      "status": "PASS (all specialties correct count)"
    },
    "cultural_diversity": {
      "aboriginal_tsi": 12,
      "lgbtqia": 40,
      "cald": 40,
      "target_aboriginal_tsi": 12,
      "target_lgbtqia": 40,
      "target_cald": 40,
      "cultural_liaison_review_complete": true,
      "status": "PASS (cultural representation correct, liaison reviews complete)"
    }
  },

  "failed_personas": [
    {
      "persona_id": "cardiology_023_af_male_70",
      "failures": [
        "RAG citation confidence 0.58 < 0.65 threshold (symptom: Palpitations)",
        "Only 1 FRACP review (minimum 2 required)"
      ],
      "recommendation": "REJECT - Request MED-001 to add additional RAG citation and second FRACP review"
    },
    {
      "persona_id": "psychiatry_018_aboriginal_depression_female_30",
      "failures": [
        "Missing cultural liaison review (Aboriginal persona - MANDATORY)",
        "Potential stereotype detected: 'non-compliant' in Aboriginal persona"
      ],
      "recommendation": "REJECT - Request MED-011 cultural safety review before deployment"
    }
  ],

  "quality_issues": [
    "8 personas below RAG citation threshold (0.65)",
    "12 personas missing second FRACP review",
    "3 Aboriginal personas missing cultural liaison review",
    "2 LGBTQIA+ personas missing educator review"
  ],

  "clinical_inaccuracies": [
    "cardiology_034: Aspirin prescribed in active peptic ulcer (contraindicated)",
    "obgyn_012: Warfarin prescribed in pregnancy (teratogenic)"
  ],

  "cultural_safety_violations": [
    "psychiatry_018: 'Non-compliant' stereotype in Aboriginal persona",
    "cardiology_041: Generic 'Aboriginal' without Nation specification"
  ],

  "security_violations": [],

  "recommendation": "CONDITIONAL APPROVAL",
  "deployment_readiness": "97.8%",
  "next_steps": [
    "Fix 8 failed personas (RAG citations, FRACP reviews, cultural liaison reviews)",
    "Re-submit for QA-001 validation",
    "Once 100% pass rate achieved → APPROVED FOR DEPLOYMENT"
  ]
}
```

---

## Validation Checklist (13 Quality Gates)

**All 360 personas must pass ALL 13 gates**:

1. [ ] **JSON Template Compliance**: All required fields present
2. [ ] **RAG Citations >0.65**: All symptoms have eTG/AMH/textbook citations with confidence >0.65
3. [ ] **FRACP Reviews ≥2**: Each persona has ≥2 specialist clinician reviews with "Approved: Yes"
4. [ ] **Clinical Accuracy**: Zero wrong diagnoses, dangerous advice, contraindicated medications
5. [ ] **Australian Medical Context**: eTG/AMH guidelines, PBS restrictions, Medicare billing, AHPRA standards
6. [ ] **Difficulty Distribution**: 125 Easy (35%), 148 Medium (41%), 87 Hard (24%)
7. [ ] **Specialty Distribution**: Correct allocation per specialty (45 cardiology, 45 emergency, etc.)
8. [ ] **Cultural Safety - Aboriginal/TSI**: 12 personas (3.3%), NO stereotypes, Nation specified, cultural liaison review ✓
9. [ ] **Cultural Safety - LGBTQIA+**: 40 personas (11%), correct pronouns, no stereotypes, educator review ✓
10. [ ] **Cultural Safety - CALD**: 40 personas (11%), NO stereotypes, diverse backgrounds, interpreter services
11. [ ] **Zero Hardcoded Credentials**: No API keys, database passwords, file paths in JSON
12. [ ] **Zero Security Violations**: PHI properly anonymized, no real patient data
13. [ ] **Educational Alignment**: AMC competencies covered, learning objectives clear

---

## Validation Workflow

**Step 1: Batch Validation** (per specialty):
```python
# Validate all 45 cardiology personas from MED-001
qa_results_cardiology = []
for persona in cardiology_personas:
    result = validate_persona(persona)  # Runs all 13 quality gates
    qa_results_cardiology.append(result)

# Generate specialty report
specialty_report = generate_specialty_report(qa_results_cardiology)
# Cardiology: 42/45 PASS (3 failed - RAG citations low)
```

**Step 2: Cross-Specialty Validation**:
```python
# Check distribution across all 360 personas
validate_difficulty_distribution(all_personas)  # 125 Easy, 148 Medium, 87 Hard
validate_specialty_distribution(all_personas)   # 45 cardiology, 45 emergency, etc.
validate_cultural_distribution(all_personas)    # 12 Aboriginal, 40 LGBTQIA+, 40 CALD
```

**Step 3: Generate QA Report**:
```python
qa_report = {
    "pass_rate": calculate_pass_rate(all_personas),  # 352/360 = 97.8%
    "failed_personas": identify_failures(all_personas),  # 8 personas failed
    "recommendation": "CONDITIONAL APPROVAL" if pass_rate < 100 else "APPROVED FOR DEPLOYMENT"
}
```

**Step 4: Iterative Improvement**:
```markdown
QA Report → Failed Personas → Return to Specialist Agent → Fix Issues → Re-validate → Repeat until 100% pass rate
```

---

## Critical Error Auto-Fail

**Immediate REJECT** (no discussion):

1. **Security Violations**:
   - API keys, database credentials, file paths in JSON → IMMEDIATE REJECT

2. **Clinical Inaccuracies**:
   - Contraindicated medications (aspirin in active bleeding, warfarin in pregnancy) → REJECT
   - Dangerous advice (NSAIDs in AKI, beta-blockers in severe asthma) → REJECT

3. **Cultural Safety Violations**:
   - Stereotypes in Aboriginal/TSI personas → REJECT
   - Wrong pronouns/deadnaming in LGBTQIA+ personas → REJECT

4. **Missing Mandatory Reviews**:
   - Aboriginal/TSI persona without cultural liaison review → REJECT
   - LGBTQIA+ persona without educator review → REJECT

---

## Example Validation (Single Persona)

**Input**: `cardiology_001_stemi_male_65.json`

**Validation Result**:
```json
{
  "persona_id": "cardiology_001_stemi_male_65",
  "validation_status": "PASS",
  "validations_performed": 13,
  "validations_passed": 13,
  "validations_failed": 0,
  "issues": [],

  "technical_compliance": {
    "json_template": "PASS (all required fields present)",
    "rag_citations": "PASS (8 citations, avg confidence 0.76)",
    "fracp_reviews": "PASS (2 reviews, both approved)"
  },

  "clinical_accuracy": {
    "diagnosis": "STEMI - Correct ✓",
    "management": "Aspirin 300mg STAT, clopidogrel, thrombolysis - Correct ✓",
    "critical_errors_defined": "Yes (missed STEMI, delayed aspirin) ✓",
    "status": "PASS"
  },

  "cultural_safety": {
    "cultural_background": "None (mainstream Australian)",
    "stereotypes": "N/A",
    "status": "PASS"
  },

  "educational_quality": {
    "difficulty": "Medium (appropriate for STEMI)",
    "complexity": "Appropriate (8 symptoms, 3 comorbidities)",
    "status": "PASS"
  },

  "security": {
    "credentials_detected": "None",
    "phi_anonymized": "Yes",
    "status": "PASS"
  },

  "recommendation": "APPROVED FOR DEPLOYMENT"
}
```

---

## Summary

**QA-001 medical-qa-validator** validates all 360 personas with:
- ✅ 13 quality gates (JSON, RAG, FRACP, clinical, cultural, educational, security)
- ✅ Comprehensive QA report (pass rate, failed personas, recommendations)
- ✅ Critical error auto-fail (security, clinical inaccuracies, cultural violations)
- ✅ Iterative improvement loop (fix failed personas → re-validate → 100% pass rate)
- ✅ Deployment readiness score (97.8% → 100%)
- ✅ Zero tolerance for security/safety violations

**Next Steps**:
1. Run QA-001 validation on all 360 personas
2. Generate comprehensive QA report
3. Fix failed personas (return to specialist agents)
4. Re-validate until 100% pass rate
5. Deploy to production database

---

**Status**: ✅ AGENT SPECIFICATION COMPLETE
**Last Updated**: 2026-03-15
**Version**: 1.0
