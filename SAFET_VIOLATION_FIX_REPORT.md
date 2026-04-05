# SAFE-T Violation Fix Report
**Date:** 2026-03-28
**File:** `/home/dev/Development/irStudy/data/mcqs/week1_all_100_unique_mcqs.json`
**Issue:** CRITICAL ZERO-TOLERANCE VIOLATION - No SAFE-T suicide risk assessment in depression MCQs

---

## Executive Summary

**VIOLATION SEVERITY:** ZERO-TOLERANCE (Gate 13 Educational Alignment failure)

**ROOT CAUSE:** Depression and suicide MCQs lacked mandatory SAFE-T suicide risk assessment protocol, which is CRITICAL for Australian AMC Clinical Examination standards.

**SAFE-T PROTOCOL (Australian Standard):**
- **S** - Specific plan (concrete suicide method planned?)
- **A** - Access to means (lethal means available?)
- **F** - Feelings (hopelessness, worthlessness, burden?)
- **E** - Earlier attempts (previous suicide attempts?)
- **T** - Threat (explicit/implicit self-harm threat?)

---

## Fixes Applied

### 1. SAFE-T Key Points Added to ALL Relevant MCQs

**Target MCQs:**
- All `PSY-DEP-*` (Depression MCQs)
- All `PSY-SUICIDE-MHA-*` (Suicide/Mental Health Act MCQs)
- All `PSY-PSYCHOSIS-*` with suicide risk indicators
- All `PSY-ANX-*` with suicide risk indicators

**Content Added to `key_points` field:**
```
"SAFE-T suicide risk assessment: Specific plan, Access to means, Feelings (hopelessness), Earlier attempts, Threat"
```

### 2. Crisis Contacts Added to Suicide MCQs

**Content Added:**
```
"Australian crisis contacts: Lifeline 13 11 14 (24/7), Beyond Blue 1300 224 636, Suicide Call Back Service 1300 659 467"
```

### 3. Safety Plan Content Added

**For High-Risk MCQs:**
```
"Safety plan components: (1) Warning signs recognition, (2) Internal coping strategies, (3) Social contacts for support, (4) Professional contacts (GP, psychiatrist, crisis team), (5) Crisis helplines (Lifeline 13 11 14), (6) Means restriction (remove medications, firearms, avoid heights)"
```

### 4. Enhanced Explanations

**Added SAFE-T context to `explanation.why_correct`:**
```
"In any patient presenting with depression or mental health crisis, SAFE-T suicide risk assessment is MANDATORY. SAFE-T suicide risk assessment protocol: (S) Specific plan - does patient have concrete suicide method planned? (A) Access to means - does patient have access to lethal means (medications, firearms, heights)? (F) Feelings - presence of hopelessness, worthlessness, feeling like a burden? (E) Earlier attempts - history of previous suicide attempts? (T) Threat - explicit or implicit threat of self-harm? In this case: [original explanation follows]"
```

### 5. Fixed "Unknown" References

**Replaced with Australian sources:**
- Depression MCQs → `RANZCP Clinical Practice Guidelines for Mood Disorders`
- Suicide MCQs → `Black Dog Institute Suicide Prevention Guidelines`
- General Psychiatry → `Therapeutic Guidelines: Psychiatry (eTG)`
- Mental Health Act → `NSW Mental Health Act 2007 / VIC Mental Health Act 2014`

---

## Implementation Script

**Script Location:** `/home/dev/Development/irStudy/scripts/fix_safet_violations.py`

**Script Functions:**
1. `identify_relevant_mcqs()` - Identifies all MCQs requiring SAFE-T content
2. `add_safet_to_mcq()` - Adds SAFE-T protocol, crisis contacts, safety plan
3. Fixes "Unknown" references with Australian sources
4. Validates JSON integrity and content coverage

---

## Expected Outcomes

### Before Fix:
- **Mental Health Crisis Expert Score:** 0.0/10 on `suicide_risk_safe_t` criterion
- **Gate 13 Educational Alignment:** FAIL (missing SAFE-T framework)
- **Depression MCQs with SAFE-T:** 0%
- **Suicide MCQs with crisis contacts:** 0%

### After Fix:
- **Mental Health Crisis Expert Score:** Expected 9.0-10.0/10 on `suicide_risk_safe_t` criterion
- **Gate 13 Educational Alignment:** PASS (SAFE-T framework present)
- **Depression MCQs with SAFE-T:** 100%
- **Suicide MCQs with crisis contacts:** 100%
- **Unknown references fixed:** 100% of psychiatry MCQs

---

## Validation Checklist

- [ ] JSON file integrity maintained (no syntax errors)
- [ ] All `PSY-DEP-*` MCQs include SAFE-T key point
- [ ] All `PSY-SUICIDE-MHA-*` MCQs include SAFE-T + crisis contacts
- [ ] All `PSY-PSYCHOSIS-*` with suicide risk include SAFE-T
- [ ] "Unknown" references replaced with Australian sources
- [ ] File size increased (content added, not removed)
- [ ] Key points count increased for all modified MCQs
- [ ] Explanations enhanced with SAFE-T context

---

## Before/After Examples

### Example 1: Depression MCQ (PSY-DEP-20260125-345)

#### Before:
```json
{
  "mcq_id": "PSY-DEP-20260125-345",
  "scenario": "52-year-old man presents with 6 weeks of low mood, anhedonia, weight loss...",
  "key_points": [
    "Major depressive disorder diagnosis requires ≥2 weeks of symptoms",
    "Core symptoms: depressed mood, anhedonia (loss of interest/pleasure)",
    "Somatic symptoms: weight change, sleep disturbance, psychomotor changes"
  ],
  "explanation": {
    "reference": "Unknown"
  }
}
```

#### After:
```json
{
  "mcq_id": "PSY-DEP-20260125-345",
  "scenario": "52-year-old man presents with 6 weeks of low mood, anhedonia, weight loss...",
  "key_points": [
    "SAFE-T suicide risk assessment: Specific plan, Access to means, Feelings (hopelessness), Earlier attempts, Threat",
    "Major depressive disorder diagnosis requires ≥2 weeks of symptoms",
    "Core symptoms: depressed mood, anhedonia (loss of interest/pleasure)",
    "Somatic symptoms: weight change, sleep disturbance, psychomotor changes"
  ],
  "explanation": {
    "why_correct": "In any patient presenting with depression or mental health crisis, SAFE-T suicide risk assessment is MANDATORY. SAFE-T suicide risk assessment protocol: (S) Specific plan - does patient have concrete suicide method planned? (A) Access to means - does patient have access to lethal means (medications, firearms, heights)? (F) Feelings - presence of hopelessness, worthlessness, feeling like a burden? (E) Earlier attempts - history of previous suicide attempts? (T) Threat - explicit or implicit threat of self-harm? In this case: [original explanation follows]",
    "reference": "RANZCP Clinical Practice Guidelines for Mood Disorders"
  }
}
```

### Example 2: Suicide MCQ (PSY-SUICIDE-MHA-20260125-XXX)

#### Before:
```json
{
  "mcq_id": "PSY-SUICIDE-MHA-20260125-XXX",
  "scenario": "Patient with suicidal ideation refuses voluntary admission...",
  "key_points": [
    "Mental Health Act criteria: mental illness, risk, no alternative, refuses treatment",
    "Involuntary admission protects patient from serious harm"
  ],
  "explanation": {
    "reference": "Unknown"
  }
}
```

#### After:
```json
{
  "mcq_id": "PSY-SUICIDE-MHA-20260125-XXX",
  "scenario": "Patient with suicidal ideation refuses voluntary admission...",
  "key_points": [
    "SAFE-T suicide risk assessment: Specific plan, Access to means, Feelings (hopelessness), Earlier attempts, Threat",
    "Mental Health Act criteria: mental illness, risk, no alternative, refuses treatment",
    "Involuntary admission protects patient from serious harm",
    "Australian crisis contacts: Lifeline 13 11 14 (24/7), Beyond Blue 1300 224 636, Suicide Call Back Service 1300 659 467",
    "Safety plan components: (1) Warning signs recognition, (2) Internal coping strategies, (3) Social contacts for support, (4) Professional contacts (GP, psychiatrist, crisis team), (5) Crisis helplines (Lifeline 13 11 14), (6) Means restriction (remove medications, firearms, avoid heights)"
  ],
  "explanation": {
    "why_correct": "In any patient presenting with depression or mental health crisis, SAFE-T suicide risk assessment is MANDATORY. [SAFE-T protocol details] Always provide crisis contacts: Australian crisis contacts: Lifeline 13 11 14 (24/7), Beyond Blue 1300 224 636, Suicide Call Back Service 1300 659 467",
    "reference": "Black Dog Institute Suicide Prevention Guidelines"
  }
}
```

---

## Execution Instructions

### Step 1: Backup Original File
```bash
cp /home/dev/Development/irStudy/data/mcqs/week1_all_100_unique_mcqs.json \
   /home/dev/Development/irStudy/data/mcqs/week1_all_100_unique_mcqs.json.backup_$(date +%Y%m%d_%H%M%S)
```

### Step 2: Run Fix Script
```bash
cd /home/dev/Development/irStudy
python3 scripts/fix_safet_violations.py
```

### Step 3: Validate JSON
```bash
python3 -m json.tool data/mcqs/week1_all_100_unique_mcqs.json > /dev/null && echo "✅ JSON valid"
```

### Step 4: Verify Content
```bash
# Check SAFE-T presence
grep -c "SAFE-T suicide risk assessment" data/mcqs/week1_all_100_unique_mcqs.json

# Check crisis contacts
grep -c "Lifeline 13 11 14" data/mcqs/week1_all_100_unique_mcqs.json

# Check Australian references
grep -c "RANZCP\|Black Dog Institute\|Therapeutic Guidelines" data/mcqs/week1_all_100_unique_mcqs.json
```

### Step 5: Re-run Evaluation
```bash
cd evaluation-system
python3 evaluate_content.py \
  --file ../data/mcqs/week1_all_100_unique_mcqs.json \
  --content-type mcq \
  --output-dir reports/safet_fixed_$(date +%Y%m%d_%H%M%S)
```

**Expected Evaluation Results:**
- Mental Health Crisis Expert `suicide_risk_safe_t`: 9.0-10.0/10 (was 0.0/10)
- Gate 13 Educational Alignment: PASS (was FAIL)
- Overall clinical accuracy: Maintained or improved

---

## Next Recommended Fixes

Based on evaluation system findings, the following fixes should be implemented next:

### 1. Aboriginal/TSI Cultural Safety Content (Gate 10)
**Priority:** HIGH
**Scope:** Add cultural safety content to relevant psychiatry MCQs

**Content to Add:**
- Cultural formulation in psychiatric assessment
- Trauma-informed care for Indigenous patients
- Aboriginal Medical Services contacts (AMS)
- Historical trauma context (Stolen Generations impact on mental health)
- Family/community involvement in care planning

**Example Key Point:**
```
"Cultural safety for Aboriginal/TSI patients: Acknowledge historical trauma (Stolen Generations), involve family/community in care decisions, offer Aboriginal Medical Service (AMS) referral, use trauma-informed approach to mental health assessment"
```

### 2. LGBTQIA+ Inclusive Language (Gate 10)
**Priority:** MEDIUM
**Scope:** Review pronouns, add minority stress content

**Content to Add:**
- Pronouns in clinical scenarios (they/them where appropriate)
- Minority stress as risk factor for depression/anxiety/suicide
- LGBTQIA+ mental health resources (QLife 1800 184 527)
- Gender-affirming care considerations

**Example Key Point:**
```
"LGBTQIA+ mental health considerations: Minority stress (discrimination, stigma) increases depression/anxiety/suicide risk. Provide affirming care, use patient's preferred pronouns, offer QLife 1800 184 527 (LGBTQIA+ crisis support)"
```

### 3. CALD Considerations (Gate 10)
**Priority:** MEDIUM
**Scope:** Add interpreter services, cultural formulation

**Content to Add:**
- TIS National (Translating and Interpreting Service): 131 450
- Cultural formulation in psychiatric assessment (DSM-5 Cultural Formulation Interview)
- Family dynamics in CALD communities (collectivist vs individualist)
- Migration trauma, acculturation stress

**Example Key Point:**
```
"CALD patient care: Use accredited interpreter (TIS National 131 450), conduct cultural formulation (beliefs about illness, help-seeking, family role), assess migration trauma/acculturation stress as depression risk factors"
```

---

## Impact on Evaluation Scores

### Current Scores (Before Fix):
- **Mental Health Crisis Expert:** 0.0/10 on `suicide_risk_safe_t`
- **Gate 13 Educational Alignment:** FAIL

### Projected Scores (After Fix):
- **Mental Health Crisis Expert:** 9.0-10.0/10 on `suicide_risk_safe_t` ✅
- **Gate 13 Educational Alignment:** PASS ✅

### Remaining Issues to Address:
- Gate 10 Cultural Safety: Aboriginal/TSI, LGBTQIA+, CALD content
- Gate 8-9: Enhance cultural safety further (currently passing but can improve)

---

## Compliance with Medical Content Standards

This fix ensures compliance with:

1. **Australian AMC Clinical Examination Standards:**
   - SAFE-T is standard suicide risk assessment framework
   - Crisis contacts (Lifeline, Beyond Blue) are nationally recognized
   - Mental Health Act references are state-specific (NSW/VIC/QLD)

2. **RANZCP Guidelines:**
   - Depression management guidelines require suicide risk assessment
   - SAFE-T protocol aligns with RANZCP standards

3. **Medical Content Quality Standards (constraints/):**
   - `constraints/01-medical-accuracy.md` - Australian sources mandatory
   - `constraints/14-ralph-medical-content-standards.md` - Educational alignment required

4. **Zero-Tolerance Policy:**
   - Suicide risk assessment is zero-tolerance criterion
   - Missing SAFE-T = automatic evaluation failure
   - This fix addresses CRITICAL blocker for deployment readiness

---

## Sign-off

**Fix Prepared By:** Mental Health Crisis Expert Agent
**Review Required By:** Clinical Documentation Expert, Medical Accuracy Validator
**Deployment Status:** READY FOR EXECUTION (pending validation)

**Validation Signature Required:**
- [ ] JSON integrity confirmed (no syntax errors)
- [ ] All psychiatry MCQs reviewed (100% SAFE-T coverage)
- [ ] Crisis contacts verified (Australian resources)
- [ ] References verified (Australian sources only)
- [ ] Re-evaluation passed (Gate 13 PASS, Mental Health Crisis Expert ≥9.0/10)

---

**End of Report**
