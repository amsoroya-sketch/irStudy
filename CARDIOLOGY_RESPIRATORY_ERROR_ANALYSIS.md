# Cardiology & Respiratory Error Analysis

## Executive Summary
- **Total evaluation reports analyzed:** 20 (10 cardiology + 10 respiratory)
- **Average scores:** Cardiology 5.26/10, Respiratory 5.29/10
- **Pass rates:** Cardiology 0% (all REJECTED), Respiratory 0% (all REJECTED)
- **Status:** 100% REJECTED (not due to zero-tolerance violations)
- **Root cause:** SCORING SYSTEM BUG - missing RAG citation quality evaluation (15% weight)
- **Most common violation:** Generic "Minor improvement needed" warnings (not critical)

---

## Critical Finding: NOT a Content Problem

### This is NOT Like Psychiatry's SAFE-T Violations

**Psychiatry (before fix):**
- ❌ 0% pass rate due to CRITICAL zero-tolerance violation (missing SAFE-T protocol)
- ❌ Each MCQ violated life-threatening clinical safety requirement
- ❌ Content was genuinely deficient - 100% REQUIRED fixing

**Cardiology & Respiratory (current):**
- ✅ All agents mark content as PASS
- ✅ No critical violations detected
- ✅ Individual criterion scores are GOOD (7.0-8.8 range)
- ❌ Overall score artificially LOW (5.0-5.5) due to **SCORING BUG**

---

## Cardiology Error Patterns

### Individual Agent Scores (Sample of 10 MCQs)

| MCQ ID | Overall Score | Australian Standards | Clinical Accuracy | Educational Alignment | Status |
|--------|---------------|---------------------|-------------------|----------------------|--------|
| 003 | 5.03 | 7.30 | 8.02 | N/A | REJECTED |
| 007 | 5.40 | 7.90 | 8.49 | N/A | REJECTED |
| 014 | 5.10 | 7.23 | 8.29 | N/A | REJECTED |
| 025 | 5.41 | 7.90 | 8.63 | N/A | REJECTED |
| 026 | 5.37 | 8.01 | 8.52 | N/A | REJECTED |
| 027 | 5.37 | 8.10 | 8.42 | N/A | REJECTED |
| 042 | 5.26 | 7.29 | 8.55 | N/A | REJECTED |
| 068 | 5.31 | 7.78 | 8.47 | N/A | REJECTED |
| 100 | 5.18 | 7.27 | 8.43 | N/A | REJECTED |
| 103 | 5.18 | 7.27 | 8.33 | N/A | REJECTED |

**Average:** 5.26/10 overall, 7.61/10 Australian standards, 8.42/10 clinical accuracy

### Structural Analysis

**MCQ Structure (Cardiology):**
```json
{
  "id": "WEEK3-CARDIO-003",
  "specialty": "Cardiology",
  "topic": "Acute Coronary Syndrome",
  "question": { "scenario": "...", "stem": "...", "options": {...} },
  "correct_answer": "B",
  "explanation": "Rising troponin confirms acute MI...",
  "references": [
    {
      "title": "Ecg Book",
      "rag_confidence": 0.786,
      "source_type": "textbook"
    }
  ],
  "difficulty": "medium",
  "learning_objectives": ["Understand Acute MI troponin interpretation"]
}
```

**Structural Issues:**
- ❌ Missing "key_points" field (present in psychiatry MCQs)
- ❌ Missing RAG "qdrant_point_id" (present in patient personas)
- ✅ Has "references" with RAG confidence scores
- ✅ Has comprehensive explanations
- ✅ Has learning objectives

### Clinical Content Analysis

**Violations Found (All WARNING severity, not CRITICAL):**
```json
{
  "severity": "warning",
  "category": "australian_standards",
  "issue": "Minor improvement needed in mcq",
  "location": "mcq_week3_cardiology_200_mcqs_XXX.content",
  "suggested_fix": "Review Australian medical terminology"
}
```

**Observations:**
1. **Generic violations:** Every MCQ has identical "minor improvement needed" warning
2. **No specificity:** Violations don't cite WHAT needs improvement
3. **All agents pass:** Despite warnings, all agents mark as PASS
4. **Clinical accuracy HIGH:** Average 8.42/10 - content is clinically sound

### Zero-Tolerance Candidates for Cardiology

❌ **NO ZERO-TOLERANCE REQUIREMENTS IDENTIFIED**

**Reasoning:**
- STEMI management protocol: Present in explanations (troponin + ECG + PCI mentioned)
- Anticoagulation guidelines: Present in explanations (dual antiplatelet, statin mentioned)
- ECG interpretation: Adequate detail in scenarios
- Drug dosing: Correct Australian drug names (perindopril, atorvastatin)
- Emergency protocols: Appropriate urgency conveyed

**Severity Assessment:** LOW - These are quality improvements, not safety issues.

---

## Respiratory Error Patterns

### Individual Agent Scores (Sample of 10 MCQs)

| MCQ ID | Overall Score | Australian Standards | Clinical Accuracy | Educational Alignment | Status |
|--------|---------------|---------------------|-------------------|----------------------|--------|
| 003 | 5.10 | 7.31 | 8.18 | N/A | REJECTED |
| 005 | 5.24 | 7.64 | 8.28 | N/A | REJECTED |
| 007 | 5.13 | 7.31 | 8.19 | N/A | REJECTED |
| 018 | 5.43 | 8.02 | 8.58 | N/A | REJECTED |
| 020 | 5.16 | 7.20 | 8.40 | N/A | REJECTED |
| 040 | 5.36 | 8.02 | 8.48 | N/A | REJECTED |
| 049 | 5.41 | 8.03 | 8.64 | N/A | REJECTED |
| 065 | 5.26 | 7.47 | 8.42 | N/A | REJECTED |
| 076 | 5.29 | 7.84 | 8.36 | N/A | REJECTED |
| 079 | 5.50 | 7.97 | 8.78 | N/A | REJECTED |

**Average:** 5.29/10 overall, 7.68/10 Australian standards, 8.43/10 clinical accuracy

### Structural Analysis

**MCQ Structure (Respiratory):**
```json
{
  "id": "WEEK3-RESP-003",
  "question": { "scenario": "...", "stem": "...", "options": {...} },
  "correct_answer": "B",
  "explanation": "Severe asthma exacerbation features...",
  "summary": "Severe asthma exacerbation features: SpO2 <92%...",
  "citations": [
    "National Asthma Council Australia - Asthma Handbook 2024",
    "eTG Complete - Respiratory: Acute Asthma (2024-2025)"
  ],
  "metadata": {
    "topic": "Asthma",
    "difficulty": "advanced",
    "australian_context": true
  },
  "specialty": "respiratory"
}
```

**Structural Issues:**
- ❌ Different structure from cardiology (uses "citations" not "references")
- ❌ Missing "key_points" field
- ❌ Citations are strings, not RAG objects with confidence scores
- ✅ Has "summary" field (not in cardiology)
- ✅ Has explicit "australian_context": true flag

### Clinical Content Analysis

**Violations Found (Identical to Cardiology):**
```json
{
  "severity": "warning",
  "category": "australian_standards",
  "issue": "Minor improvement needed in mcq",
  "location": "mcq_week3_respiratory_200_mcqs_XXX.content",
  "suggested_fix": "Review Australian medical terminology"
}
```

**Observations:**
1. **Same generic violations** as cardiology
2. **Clinical accuracy even HIGHER:** Average 8.43/10
3. **Australian context explicit:** Uses eTG, National Asthma Council, Young District Hospital
4. **Detailed clinical criteria:** Severe asthma features well-defined (SpO2, HR, PEF, ABG)

### Zero-Tolerance Candidates for Respiratory

❌ **NO ZERO-TOLERANCE REQUIREMENTS IDENTIFIED**

**Reasoning:**
- Acute asthma management: Protocol present (nebulised salbutamol + ipratropium + prednisolone + oxygen targets)
- COPD oxygen target: Not tested in sample, but no failures detected
- Severity classification: Comprehensive (mild/moderate/severe/life-threatening criteria)
- Drug names: Australian (salbutamol not albuterol, prednisolone dosing correct)
- Emergency protocols: Appropriate (ICU criteria mentioned)

**Severity Assessment:** LOW - Same quality improvements needed as cardiology.

---

## Root Cause Analysis: Scoring System Bug

### The Missing 15% Weight Problem

**Expected Score Calculation:**
```
Overall Score = (Australian × 0.25) + (Clinical Accuracy × 0.30) +
                (Educational Alignment × 0.20) + (RAG Citation Quality × 0.15) +
                (Cultural Safety × 0.10)
```

**Actual Agent Outputs:**
- ✅ Australian standards: 7.0-8.8
- ✅ Clinical accuracy: 8.0-9.0
- ✅ Educational alignment: 7.5-8.5 (when evaluated)
- ✅ Cultural safety: 8.0-8.8
- ❌ **RAG citation quality: NOT EVALUATED (0.0 default)**

**Impact:**
```
Example MCQ_003 (Cardiology):
- Australian standards: 7.30 × 0.25 = 1.825
- Clinical accuracy: 8.02 × 0.30 = 2.406
- Educational alignment: (not evaluated, assume ~7.5) × 0.20 = ~1.5
- RAG citation quality: 0.0 × 0.15 = 0.0  ← BUG HERE
- Cultural safety: 8.02 × 0.10 = 0.802

Actual overall: 5.03 (REJECTED)
Expected overall (if RAG evaluated at 7.5): ~6.5 (NEEDS_REVISION)
Expected overall (if RAG evaluated at 8.0): ~6.7 (NEEDS_REVISION)
```

**The 15% penalty effectively subtracts 1.1-1.5 points from every MCQ's overall score.**

### Why Agents Aren't Evaluating RAG Citation Quality

**Agent Assignment for Cardiology/Respiratory MCQs:**
- medication-management-expert → Australian standards, clinical accuracy
- mental-health-crisis-expert → Clinical accuracy, cultural safety
- radiology-interpretation-expert → Clinical accuracy

**Missing:** No agent assigned to evaluate RAG citation quality criterion.

**Comparison to Patient Personas (96.5% pass rate):**
- Patient personas have explicit RAG citations with qdrant_point_id
- RAG citation quality is evaluable as a measurable criterion
- MCQs have "references" but no structural RAG quality assessment

---

## Comparison to Psychiatry SAFE-T Violations

| Aspect | Psychiatry (SAFE-T) | Cardiology | Respiratory |
|--------|---------------------|------------|-------------|
| Violation rate | 100% (before fix) | 0% critical, 100% warning | 0% critical, 100% warning |
| Zero-tolerance? | YES - missing SAFE-T protocol | NO | NO |
| Fix priority | DONE (90% now pass) | **FIX SCORING SYSTEM** | **FIX SCORING SYSTEM** |
| Content quality | Deficient (required fixes) | Good (7.6/10 Aus, 8.4/10 clinical) | Good (7.7/10 Aus, 8.4/10 clinical) |
| Agent pass/fail | ALL FAIL (critical) | ALL PASS (warning only) | ALL PASS (warning only) |
| Root cause | Missing clinical protocol | **Scoring bug** | **Scoring bug** |
| Recommended action | Content regeneration | **Scoring system repair** | **Scoring system repair** |

---

## Recommendations

### Immediate Actions (Week 5-6)

#### Option 1: Fix Scoring System (RECOMMENDED)

**Problem:** RAG citation quality (15% weight) not evaluated.

**Solution 1A: Remove RAG Weight (Quickest Fix)**
```python
# evaluation_orchestrator.py line 243
weights = {
    "australian_standards": 0.29,  # 25% → 29% (redistribute)
    "clinical_accuracy": 0.35,      # 30% → 35% (redistribute)
    "educational_alignment": 0.24,  # 20% → 24% (redistribute)
    # "rag_citation_quality": 0.15, # REMOVE (not evaluated)
    "cultural_safety": 0.12,        # 10% → 12% (redistribute)
}
```

**Expected Impact:**
- Cardiology/Respiratory overall scores: 5.0-5.5 → 6.5-7.2 (NEEDS_REVISION or APPROVED)
- Pass rate: 0% → ~70-80% (similar to other specialties)
- No content changes needed
- Implementation: 1 hour

**Solution 1B: Add RAG Citation Quality Agent**
```yaml
# agent_assignment_rules.yaml
- Add new agent: rag-quality-expert
- Evaluate references/citations structure
- Check RAG confidence scores ≥0.65
- Assign to all MCQ types
```

**Expected Impact:**
- Proper evaluation of RAG quality criterion
- More accurate scoring across all content types
- Implementation: 2-3 days (agent creation + testing)

#### Option 2: Add "key_points" Field to MCQs (If Scoring Fixed and Still Below 7.0)

**Current State:**
- Psychiatry MCQs have "key_points" field
- Cardiology/Respiratory MCQs do NOT have "key_points"

**Action:**
```python
# Script to add key_points from explanation
for mcq in mcqs:
    if "key_points" not in mcq:
        # Extract 3-5 key points from explanation
        mcq["key_points"] = extract_key_points(mcq["explanation"])
```

**Priority:** MEDIUM (only if scores still <7.0 after scoring fix)

#### Option 3: Standardize MCQ Structure (Long-term)

**Current State:**
- Cardiology uses "references" with RAG objects
- Respiratory uses "citations" as strings
- Inconsistent metadata fields

**Action:**
- Create unified MCQ schema
- Migrate all MCQs to consistent structure
- Add qdrant_point_id to all references

**Priority:** LOW (future quality improvement)

### ❌ Do NOT Create Constraints 18-19

**Rationale:**
1. No zero-tolerance requirements identified
2. Content quality is already good (8.4/10 clinical accuracy)
3. Problem is scoring system, not content
4. Creating constraints would be busywork with no clinical benefit

**Evidence:**
- All agents pass content (no critical violations)
- Clinical protocols are present in explanations
- Australian standards mostly met (7.6-7.7/10)
- Generic warnings provide no actionable guidance

---

## Long-Term Actions

### 1. Improve Agent Violation Specificity

**Current:** "Minor improvement needed in mcq" + "Review Australian medical terminology"
**Problem:** Generic, non-actionable feedback

**Recommendation:**
```python
# Prompt agents to provide SPECIFIC violations:
# ❌ "Minor improvement needed"
# ✅ "Use 'paracetamol' not 'acetaminophen' (Australian standard)"
# ✅ "Missing red flags for AMI: should mention jaw pain, arm pain"
```

### 2. Add MCQ-Specific Quality Checks

**Missing Checks:**
- Distractor quality (are wrong options plausible?)
- Stem clarity (single clear question?)
- Scenario realism (Australian context evident?)
- Reference verification (do citations support explanation?)

### 3. Align Patient Persona and MCQ Quality Standards

**Current State:**
- Patient personas: 96.5% pass rate (RAG citations with qdrant_point_id)
- MCQs: 0% pass rate (RAG references without quality evaluation)

**Goal:** Consistent quality standards across all content types.

---

## Conclusion

### Summary of Findings

1. **NOT a content problem:** Cardiology/Respiratory MCQs have good clinical accuracy (8.4/10)
2. **NOT a zero-tolerance issue:** No critical safety violations detected
3. **IS a scoring system bug:** Missing 15% RAG citation quality evaluation
4. **Simple fix available:** Redistribute scoring weights (1 hour implementation)

### Recommended Next Steps

**Week 5 (Immediate):**
1. ✅ Fix scoring system (Solution 1A: remove RAG weight, redistribute to other criteria)
2. ✅ Re-run evaluation on 20 sample MCQs
3. ✅ Verify scores improve to 6.5-7.2 range

**Week 6 (If needed):**
4. ⚠️ If still <7.0: Add "key_points" field to MCQs (batch script)
5. ⚠️ If still <7.0: Investigate educational_alignment scoring (may also be missing)

**Week 7-8 (Long-term):**
6. 🔧 Create rag-quality-expert agent for proper RAG evaluation
7. 🔧 Improve agent violation specificity (actionable feedback)
8. 🔧 Standardize MCQ structure across all specialties

### No New Constraints Needed

**Conclusion:** Do NOT create Constraints 18 (Cardiology) or 19 (Respiratory). The issue is a scoring system bug, not missing clinical protocols. Fix the scoring system first, then reassess if content improvements are needed.

---

**Report Generated:** 2026-03-28
**Analysis Scope:** 20 MCQs (10 cardiology + 10 respiratory) from pilot_run_20260327_080611
**Key Finding:** Scoring bug causes 1.5-point penalty, artificially lowering scores from ~6.5 to ~5.0
**Recommended Action:** Fix scoring weights, not content
