# OSCE & Study Card Analysis

**Date:** 2026-03-28
**Status:** Analysis Complete

---

## Executive Summary

**Critical Finding:** OSCEs and Study Cards have 0.0/10 scores due to **GENERATION FAILURE**, not content deficiency or system bugs.

| Content Type | Avg Score | Root Cause | Solution |
|--------------|-----------|------------|----------|
| **OSCEs** | 0.36/10 | Placeholder templates (never generated) | Full regeneration required |
| **Study Cards** | 4.77/10 | Likely similar (needs verification) | Full regeneration required |
| MCQs (Psychiatry) | 5.0/10 | Content deficiency (missing SAFE-T) | ✅ Fixed with auto-scripts |
| MCQs (Cardiology/Respiratory) | 5.0/10 | System bug (scoring weights) | ✅ Fixed with redistribution |

---

## OSCE Analysis

### Evaluation Reports (10 analyzed)

**Scores:**
- Overall: 0.0/10 (all REJECTED)
- Australian standards: 5.46/10
- Educational alignment: 8.50/10
- Clinical accuracy: 3.82/10
- **Cultural safety: 0.0/10** ← Suspicious

**Agent Feedback (Typical):**
```
"CRITICAL: Generic OSCE template without actual clinical content"
"CRITICAL: Patient presentation is template boilerplate"
"CRITICAL: All 40 use identical template structure"
"CRITICAL: Expected answers are generic templates without clinical specificity"
"CRITICAL: No SAFE-T suicide risk assessment framework present"
"CRITICAL: No medication management plan - generic 'Australian guidelines' placeholder"
```

### Actual OSCE Content

**File:** `data/osces/psychiatry_40_osces.json` (40 OSCEs)

**Example OSCE #1 (MSE - Appearance & Behavior):**

```json
{
  "patient_presentation": "A patient presents for psychiatric assessment. MSE - Appearance & Behavior. Complete the clinical assessment using provided tools.",
  "history": "Clinical history relevant to MSE - Appearance & Behavior",
  "examination_findings": "Mental status examination findings for MSE - Appearance & Behavior",
  "expected_answers": {
    "assessment": "Systematic assessment findings for MSE - Appearance & Behavior",
    "diagnosis": "Primary diagnosis: MSE - Appearance & Behavior. Differential based on presentation.",
    "management": "According to Australian guidelines for MSE - Appearance & Behavior: risk assessment, immediate management, ongoing treatment plan."
  },
  "references": [
    {
      "content": "",  // ← EMPTY
      "rag_confidence": 0.768
    }
  ]
}
```

**Analysis:** This is 100% placeholder text. No actual clinical content exists.

### Root Cause

**Generation Failure:** The OSCE generation process created template skeletons but never filled in actual clinical content.

**Evidence:**
1. **All 40 OSCEs** use identical structure with only topic names swapped
2. **All references** have empty `content` fields
3. **All patient presentations** are generic boilerplate
4. **All expected answers** are template phrases
5. **Agent consensus:** "This is a TEMPLATE, not an actual clinical case"

### Agent-Specific Issues

**Radiology-interpretation-expert:**
- Score: 0.0/10
- Issue: "Specialty mismatch - cannot evaluate psychiatry content"
- Recommendation: "Route to mental-health-crisis-expert"

**Medication-management-expert:**
- Score: 3.0/10
- Issue: "OSCE contains no medications to evaluate"
- Expected: "Olanzapine 10mg, PBS codes, dosing, monitoring"
- Actual: "According to Australian guidelines" (placeholder)

**Mental-health-crisis-expert:**
- Score: 3.5/10
- Issue: "No SAFE-T, no Mental Health Act, no MSE findings"
- Expected: Complete clinical case with specific symptoms
- Actual: Template boilerplate

### Comparison to MCQ Issues

| Aspect | OSCEs | Psychiatry MCQs | Cardiology MCQs |
|--------|-------|-----------------|-----------------|
| **Root Cause** | Generation failure (placeholders) | Content deficiency (missing SAFE-T) | System bug (scoring) |
| **Content Quality** | 0% (no content exists) | 80% (content exists, SAFE-T missing) | 100% (content complete) |
| **Fix Type** | Full regeneration | Auto-fix scripts | Weight redistribution |
| **Fix Complexity** | HIGH (regenerate 200+ OSCEs) | MEDIUM (fix 180 MCQs) | LOW (1 function change) |
| **Estimated Time** | 10-15 hours | 4-5 hours | 1 hour |

---

## Study Cards Analysis

**Note:** Study cards likely have similar issues (placeholder content). Needs verification.

**File to check:** `data/study_cards/*.json`

**Expected issues:**
- Avg score: 4.77/10 (higher than OSCEs, but still low)
- Possible: Partial content generation
- Possible: Missing clinical context or explanations

---

## Recommendations

### Immediate Actions (Do NOT Create Constraints 16-17)

**Constraints are NOT the solution** for placeholder content. Constraints fix content deficiency (like SAFE-T), not generation failure.

**Recommended Actions:**

#### 1. Verify Study Card Content (1 hour)
```bash
# Check if study cards have similar placeholder issue
python3 -c "
import json
from pathlib import Path

for file in Path('data/study_cards/').glob('*.json'):
    with open(file) as f:
        data = json.load(f)

    # Check first study card
    card = data.get('study_cards', [data])[0] if isinstance(data, dict) else data[0]

    print(f'\nFile: {file.name}')
    print(f'Front: {card.get(\"front\", \"\")[:100]}')
    print(f'Back: {card.get(\"back\", \"\")[:100]}')
    print(f'Explanation: {card.get(\"explanation\", \"\")[:100]}')
"
```

#### 2. Regenerate OSCEs (10-15 hours)

**High Priority:** OSCEs are critical for AMC Clinical Exam preparation.

**Process:**
1. Create OSCE generation PRD (following T-RALPH standards)
2. Define OSCE structure requirements:
   - Patient demographics (age, gender, background)
   - Complete presenting complaint (SOCRATES for pain)
   - Detailed history of presenting complaint
   - Complete 9-step history taking
   - Mental status examination (8 domains)
   - Specific physical examination findings
   - Red flags and safety netting
   - SAFE-T (for psychiatry)
   - Complete management plan with medications
   - Australian guidelines references (with content)

3. Generate 200+ OSCEs across specialties:
   - Psychiatry: 40 OSCEs
   - Cardiology: 50 OSCEs
   - Respiratory: 50 OSCEs
   - Other specialties: 60+ OSCEs

4. Validate each OSCE:
   - No placeholder text
   - All expected_answers have specific clinical content
   - All references have populated content fields
   - SAFE-T present for high-risk scenarios

#### 3. Regenerate Study Cards (if needed) (5-8 hours)

**Priority:** Medium (after OSCEs)

**Process:** Similar to OSCEs, but simpler structure

#### 4. Create Constraints 16-17 AFTER Regeneration

**Only create constraints once actual content exists.**

**Constraint 16: OSCE Requirements**
- Purpose: Prevent future placeholder generation
- Requirements:
  - Complete 9-step history (not "Clinical history relevant to...")
  - Specific examination findings (not "Examination findings for...")
  - Concrete management plans (not "According to Australian guidelines...")
  - SAFE-T for high-risk scenarios
  - Populated reference content fields

**Constraint 17: Study Card Requirements**
- Purpose: Ensure clinical context and depth
- Requirements:
  - Specific clinical scenarios (not generic definitions)
  - Australian drug names and PBS codes
  - RAG citations with qdrant_point_id
  - Red flags present
  - Clinical pearls with Australian context

---

## Lessons Learned

### Why This Wasn't Caught Earlier

1. **Metadata was correct:** OSCEs had `"validation_failures": []` and `"prevention_system": "PASSED"`
2. **Statistics looked normal:** `"total_osces": 40, "valid_citations": 120`
3. **Agent evaluations revealed the truth:** Only when expert agents reviewed content did placeholder issue become clear

### Prevention for Future Batches

**Add content completeness check:**

```python
def validate_osce_content(osce: dict) -> bool:
    """Check if OSCE has actual content (not placeholders)."""
    placeholder_patterns = [
        "A patient presents for",
        "Clinical history relevant to",
        "Mental status examination findings for",
        "Systematic assessment findings for",
        "According to Australian guidelines for",
    ]

    text_fields = [
        osce.get("scenario", {}).get("patient_presentation", ""),
        osce.get("scenario", {}).get("history", ""),
        osce.get("expected_answers", {}).get("assessment", ""),
    ]

    for field in text_fields:
        for pattern in placeholder_patterns:
            if pattern in field:
                return False  # Placeholder detected

    # Check reference content is not empty
    for ref in osce.get("references", []):
        if not ref.get("content", "").strip():
            return False  # Empty reference content

    return True
```

---

## Decision Matrix

| Content Type | Issue Type | Solution | Priority | Estimated Time |
|--------------|------------|----------|----------|----------------|
| **OSCEs** | Generation failure (placeholders) | Full regeneration | 🔴 CRITICAL | 10-15 hours |
| **Study Cards** | Likely similar (TBD) | Verify, then regenerate | 🟡 HIGH | 5-8 hours |
| MCQs (Psychiatry) | Content deficiency (SAFE-T) | ✅ Fixed (auto-scripts) | ✅ DONE | 0 hours |
| MCQs (Cardiology/Resp) | System bug (scoring) | ✅ Fixed (weight redistribution) | ✅ DONE | 0 hours |

---

## Next Steps (Batch 3 Revised)

### Phase 1: Content Verification (1 hour)
1. ✅ OSCEs verified: Placeholder templates (regeneration required)
2. ⏳ Study Cards: Verify content quality
3. ⏳ Patient Personas: Check if similar issues exist

### Phase 2: Content Regeneration (15-20 hours)
1. Regenerate 200+ OSCEs with actual clinical content
2. Regenerate study cards (if needed)
3. Validate no placeholder text remains

### Phase 3: Create Constraints (After Regeneration)
1. Create Constraint 16: OSCE Requirements
2. Create Constraint 17: Study Card Requirements
3. Add validation scripts to prevent future placeholders

---

**Status:** OSCE analysis complete, regeneration required before constraint creation
**Last Updated:** 2026-03-28
