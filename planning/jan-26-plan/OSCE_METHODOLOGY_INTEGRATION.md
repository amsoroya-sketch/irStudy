# OSCE Methodology Integration Plan

**Date**: 2026-01-26
**Status**: ⚠️ **GAP IDENTIFIED** - Structured OSCE Methodology NOT fully integrated
**Reference**: `OSCE_METHODOLOGY_GUIDE.html` (renamed from DR_AAMIR_METHODOLOGY_GUIDE.html)

---

## 🎯 Problem Statement

The Jan-26 execution plans reference 210 OSCEs but do NOT explicitly integrate the **Structured OSCE Methodology** (9 Core Principles, 4 Templates, 8-Step Conversion).

Current plans say "add summaries only" but existing OSCEs are **missing critical methodology compliance fields**.

---

## 📋 Current OSCE Structure (Incomplete)

**Existing fields in `data/osces/*.json`:**
```json
{
  "id": "CARDIO-OSCE-001",
  "specialty": "Cardiology",
  "topic": "Acute Coronary Syndrome",
  "scenario": {...},
  "tasks": [...],
  "expected_answers": {...},
  "references": [...],
  "difficulty": "Medium",
  "duration_minutes": 8
}
```

**Missing Methodology Compliance Fields:**
- ❌ `summary` (50-200 chars)
- ❌ `differential_diagnosis` (Principle 1)
- ❌ `examination_framework` (Principle 2)
- ❌ `time_allocation` (Principle 3 breakdown)
- ❌ `australian_context` (Principle 4 markers)
- ❌ `structured_frameworks_used` (SOCRATES, OPQRST, etc.)

---

## 🔑 9 Core OSCE Principles (from Methodology Guide)

### Principle 1: Differential-Driven Thinking
**Start with differentials FROM THE FIRST QUESTION**

**Required in OSCE:**
```json
{
  "differential_diagnosis": {
    "primary": "STEMI",
    "must_rule_out": ["Unstable angina", "Aortic dissection", "PE"],
    "questions_to_narrow": [
      "When did the chest pain start?",
      "Any radiation to left arm/jaw?",
      "Any shortness of breath?"
    ]
  }
}
```

### Principle 2: Structured Frameworks (Memorizable)
**Use specific, learnable frameworks**

**Required in OSCE:**
```json
{
  "examination_framework": "SOCRATES",
  "frameworks_applied": {
    "history": "SOCRATES for chest pain",
    "examination": "Cardiovascular examination routine",
    "investigations": "ACS protocol (ECG, troponin, CXR)"
  }
}
```

**Common Frameworks:**
- **SOCRATES**: Pain assessment
- **OPQRST**: Symptom characterization
- **SAMPLE**: History taking
- **ABC**: Emergency assessment
- **VINDICATE**: Differential diagnosis

### Principle 3: Time-Conscious Station Design
**Every station designed for EXACTLY 8 minutes**

**Required in OSCE:**
```json
{
  "duration_minutes": 8,
  "time_allocation": {
    "introduction": "30 seconds",
    "history_taking": "3 minutes",
    "examination": "2 minutes",
    "investigations_review": "1 minute",
    "diagnosis_management": "1 minute",
    "patient_questions": "30 seconds"
  }
}
```

### Principle 4: Australian Medical Context (CRITICAL)
**100% Australian terminology, drugs, guidelines**

**Required in OSCE:**
```json
{
  "australian_context": {
    "spelling": ["favour", "organisation", "paediatric"],
    "guidelines": ["eTG Cardiovascular", "RANZCP Clinical Practice Guidelines"],
    "drugs": ["Paracetamol (not acetaminophen)", "Salbutamol (not albuterol)"],
    "emergency_number": "000",
    "services": ["Medicare", "PBS", "NDSS"]
  }
}
```

### Principle 5: Image Integration
**Real medical images with systematic interpretation**

**Already implemented** in existing OSCEs ✅

### Principle 6: Mark Scheme Transparency
**Clear marking criteria (what gets marks, what doesn't)**

**Required enhancement:**
```json
{
  "marking_scheme": {
    "total_marks": 20,
    "breakdown": {
      "history_taking": {
        "marks": 8,
        "criteria": [
          "Asked about onset (1 mark)",
          "Character of pain (1 mark)",
          "Radiation (1 mark)",
          ...
        ]
      },
      "examination": {...},
      "diagnosis": {...}
    }
  }
}
```

### Principle 7: Real Exam Language
**Use EXACT AMC clinical exam wording**

### Principle 8: Progressive Disclosure
**Information revealed step-by-step**

### Principle 9: Safety Netting
**Always include management and follow-up**

---

## 🛠️ Required Updates to Jan-26 Plans

### Phase 4: OSCE Enhancement (Week 4, Days 19-21)

**NOT just "add summaries" - FULL methodology integration required!**

#### Day 19: OSCE Methodology Compliance (Batch 1)
**Target**: 70 OSCEs enhanced
**Specialties**: Cardiology (50) + Respiratory (20)

**Tasks**:
1. Add `summary` field (50-200 chars)
2. Add `differential_diagnosis` structure (Principle 1)
3. Add `examination_framework` (Principle 2)
4. Add detailed `time_allocation` (Principle 3)
5. Add `australian_context` markers (Principle 4)
6. Enhance `marking_scheme` transparency (Principle 6)
7. Validate all changes with QA-OSCE validator

**Script to create**:
```bash
scripts-jan-26/enhance_osces_methodology_batch1.py
```

**Validation**:
```bash
scripts/validate_osce_methodology_compliance.py \
  --input data-jan-26/osces/cardiology_enhanced.json \
  --check-principles 1,2,3,4,6
```

#### Day 20: OSCE Methodology Compliance (Batch 2)
**Target**: 70 OSCEs enhanced
**Specialties**: Psychiatry (53) + Emergency (17)

#### Day 21: OSCE Methodology Compliance (Batch 3)
**Target**: 70 OSCEs enhanced
**Specialties**: Remaining specialties

---

## 📊 Updated OSCE Target Structure

```json
{
  "id": "CARDIO-OSCE-001-ENHANCED",
  "specialty": "Cardiology",
  "topic": "Acute Coronary Syndrome",
  "subtopic": "STEMI",
  "scenario_type": "Emergency Presentation",

  "scenario": {
    "patient_presentation": "...",
    "images": [...]
  },

  "differential_diagnosis": {
    "primary": "STEMI",
    "must_rule_out": ["Unstable angina", "Aortic dissection", "PE"],
    "questions_to_narrow": ["..."]
  },

  "examination_framework": "SOCRATES + Cardiovascular examination",
  "frameworks_applied": {
    "history": "SOCRATES for chest pain",
    "examination": "CVS examination routine",
    "investigations": "ACS protocol"
  },

  "time_allocation": {
    "introduction": "30 seconds",
    "history_taking": "3 minutes",
    "examination": "2 minutes",
    "investigations_review": "1 minute",
    "diagnosis_management": "1 minute",
    "patient_questions": "30 seconds"
  },

  "australian_context": {
    "spelling": ["favour", "organisation"],
    "guidelines": ["eTG Cardiovascular"],
    "drugs": ["Aspirin", "GTN", "Morphine"],
    "emergency_number": "000",
    "services": ["Medicare", "PBS"]
  },

  "tasks": [...],
  "expected_answers": {...},

  "marking_scheme": {
    "total_marks": 20,
    "breakdown": {...}
  },

  "summary": "STEMI presentation requiring immediate ECG, troponin, and PCI discussion per eTG guidelines (8-minute station with differential-driven approach)",

  "references": [...],
  "difficulty": "Medium",
  "duration_minutes": 8,
  "generated_at": "...",
  "methodology_compliant": true,
  "methodology_version": "2026-01-structured-osce"
}
```

---

## ✅ Validation Checklist

For each enhanced OSCE, verify:

- [ ] **Summary** (50-200 chars, mentions key learning point)
- [ ] **Differential Diagnosis** (Principle 1: primary + must-rule-out + questions)
- [ ] **Examination Framework** (Principle 2: named framework like SOCRATES)
- [ ] **Time Allocation** (Principle 3: 8-minute breakdown)
- [ ] **Australian Context** (Principle 4: spelling, drugs, guidelines, 000)
- [ ] **Marking Scheme** (Principle 6: transparent criteria)
- [ ] **References** (3 citations, rag_confidence >0.70)

---

## 🔧 Implementation Scripts Needed

### 1. OSCE Enhancement Script
**File**: `scripts-jan-26/enhance_osces_with_methodology.py`

**Features**:
- Read existing OSCE JSON files
- Apply Agent OS medical experts for specialty-specific enhancements
- Add methodology compliance fields
- Preserve existing valid content
- Validate enhanced structure
- Output to `data-jan-26/osces/[specialty]_enhanced.json`

### 2. OSCE Methodology Validator
**File**: `scripts/validate_osce_methodology_compliance.py`

**Checks**:
- All 9 principles present
- Field structure correctness
- Australian context markers
- Summary length (50-200 chars)
- Time allocation adds up to 8 minutes
- Exit code 2 if non-compliant (blocks commit)

---

## 📅 Updated Timeline

### Original Plan (INCOMPLETE):
- Week 4, Day 12: "Add OSCE summaries" (2-3 hours)

### Corrected Plan (METHODOLOGY-COMPLIANT):
- **Week 4, Days 19-21**: OSCE Methodology Enhancement (3 days)
  - Day 19: Batch 1 (70 OSCEs - Cardiology + Respiratory)
  - Day 20: Batch 2 (70 OSCEs - Psychiatry + Emergency)
  - Day 21: Batch 3 (70 OSCEs - Remaining)
- **Estimated Time**: 8 hours per day × 3 days = 24 hours total
- **Deliverable**: 210 methodology-compliant OSCEs

---

## 🎯 Success Criteria

**OSCE enhancement is COMPLETE when:**

1. All 210 OSCEs have `summary` field
2. All 210 OSCEs have `differential_diagnosis` (Principle 1)
3. All 210 OSCEs have `examination_framework` (Principle 2)
4. All 210 OSCEs have detailed `time_allocation` (Principle 3)
5. All 210 OSCEs have `australian_context` markers (Principle 4)
6. All 210 OSCEs pass `validate_osce_methodology_compliance.py`
7. Pre-commit hook enforces methodology compliance
8. HTML conversion includes all new fields

---

## 📝 Key References

1. **Methodology Guide**: `OSCE_METHODOLOGY_GUIDE.html`
2. **Existing OSCEs**: `data/osces/cardiology_50_osces.json` (etc.)
3. **Agent OS Experts**: MED-001 through MED-010 (specialty-specific knowledge)
4. **Constraints**: All existing MCQ constraints apply to OSCEs
5. **Australian Standards**: eTG, RANZCP, AMH, AHPRA, PBS, Medicare, 000

---

## ⚠️ Critical Action Required

**Before proceeding with Week 4 execution:**

1. ✅ Acknowledge this gap in current plans
2. Update PER_DAY_EXECUTION_PLAN.md to reflect 3-day OSCE enhancement (not 2-3 hours)
3. Create `enhance_osces_with_methodology.py` script
4. Create `validate_osce_methodology_compliance.py` validator
5. Test enhancement on 1 sample OSCE first
6. Update pre-commit hook to validate OSCE methodology

---

**Document Status**: ⚠️ Gap Identified - Requires Plan Update
**Date**: 2026-01-26
**Impact**: Week 4 timeline extended from 2-3 hours to 3 days (24 hours)
**Next Step**: Update PER_DAY_EXECUTION_PLAN.md with corrected OSCE enhancement workflow
