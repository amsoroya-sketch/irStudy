# Week 2 Day 3 - MCQ Duplication Bug Analysis

**Date:** 2026-01-25
**Status:** ✅ Root Cause Identified
**Severity:** HIGH (65/100 entries are duplicates)

---

## Executive Summary

**Bug:** MCQ generation scripts create 65 duplicate entries (35 unique MCQs out of 100 total)

**Root Cause:** Two compounding issues:
1. **ID generation uses hash(subtopic)** - Same subtopic = same ID
2. **One template per subtopic** - Same subtopic = identical MCQ content

**Impact:**
- Week 1 goal: 100 unique MCQs
- Week 1 actual: 35 unique MCQs (65% duplication rate)
- All metrics (Tier rates, validation coverage) calculated on wrong baseline

**Fix Complexity:** Medium (requires both ID generation fix and template expansion)

---

## Detailed Analysis

### Issue 1: ID Generation Bug

**Location:** `scripts/generate_day1_mcqs.py` line 194

```python
# BUGGY CODE:
mcq_id = f"PSY-DEP-{datetime.now().strftime('%Y%m%d')}-{hash(subtopic) % 1000:03d}"
#                                                        ^^^^^^^^^^^^^^^^^^^
#                                                        Always same for same subtopic!
```

**Problem:**
- `hash("major_depressive_disorder_diagnosis")` returns the same value every time
- When generating 5 MCQs with subtopic "major_depressive_disorder_diagnosis", all get ID: `PSY-DEP-20260125-345`
- Result: 5 identical IDs in the same file

**Example:**
```python
# Batch 1: MDD Diagnosis (5 MCQs)
for i in range(5):  # ← Loop counter 'i' exists but NEVER USED
    mcq = self.generate_depression_mcq("major_depressive_disorder_diagnosis", difficulty="medium")
    all_mcqs.append(mcq)
    # All 5 MCQs get ID: PSY-DEP-20260125-345 (same hash)
```

**Evidence from Data:**
```
PSY-DEP-20260125-345: appears 5 times (all in psychiatry_depression_day1.json)
PSY-DEP-20260125-602: appears 5 times (all in psychiatry_depression_day1.json)
PSY-ANX-BIP-20260125-197: appears 5 times (all in psychiatry_anxiety_bipolar_day2.json)
```

### Issue 2: Single Template Per Subtopic

**Location:** `scripts/generate_day1_mcqs.py` lines 116-182

**Problem:** Each subtopic has exactly ONE hardcoded template

```python
mcq_templates = {
    "major_depressive_disorder_diagnosis": {
        "scenario": "A 45-year-old woman presents to her GP with 6 weeks...",
        # ^^^ Only ONE scenario for this subtopic
        "stem": "What is the most appropriate diagnosis?",
        "options": {...},  # Only ONE set of options
        "correct": "B",
        "explanation": "..."
    },
    # ... more subtopics, each with ONE template
}
```

**Impact:**
- Generate 5 MCQs with subtopic "major_depressive_disorder_diagnosis"
- All 5 use the EXACT SAME template
- Result: Not just duplicate IDs, but IDENTICAL content (scenario, options, explanation)

**This explains:**
- psychiatry_depression_day1.json: 20 entries, only 5 unique
  - 5 MCQs for "major_depressive_disorder_diagnosis" (all identical)
  - 5 MCQs for "antidepressant_selection_ssri" (all identical)
  - 3 MCQs for "treatment_resistant_depression" (all identical)
  - 4 MCQs for "depression_in_elderly" (all identical)
  - 3 MCQs for "postpartum_depression" (all identical)
  - **Total: 20 entries, 5 unique MCQs**

### Per-File Duplication Pattern

| File | Total Entries | Unique IDs | Duplicates | Pattern |
|------|---------------|------------|------------|---------|
| Day 1 (Depression) | 20 | 5 | 15 | 5 subtopics × 1 template = 5 unique |
| Day 2 (Anxiety/Bipolar) | 20 | 6 | 14 | 6 subtopics × 1 template = 6 unique |
| Day 3 (Psychosis) | 25 | 9 | 16 | 9 subtopics × 1 template = 9 unique |
| Day 4 (Suicide/MHA) | 20 | 8 | 12 | 8 subtopics × 1 template = 8 unique |
| Day 5 (Mixed Topics) | 15 | 7 | 8 | 7 subtopics × 1 template = 7 unique |
| **TOTAL** | **100** | **35** | **65** | **65% duplication** |

---

## Why This Happened

### Design Flaw

The generation script was designed as:

```python
# INTENDED DESIGN (assumed):
# "Generate 5 DIFFERENT MCQs about MDD diagnosis"
# → 5 unique scenarios, 5 unique option sets
# → MCQ 1: Patient A with presentation X
# → MCQ 2: Patient B with presentation Y
# → MCQ 3: Patient C with presentation Z
# → etc.

# ACTUAL IMPLEMENTATION:
# "Generate 5 MCQs using THE SAME template"
# → Uses hash(subtopic) for ID → all get same ID
# → Uses mcq_templates[subtopic] → all get same content
# → MCQ 1-5: ALL IDENTICAL
```

### Why Loop Counter Wasn't Used

```python
for i in range(5):
    # Loop variable 'i' available but NEVER USED
    mcq = self.generate_depression_mcq("major_depressive_disorder_diagnosis", difficulty="medium")
    #                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #                                   Same subtopic every iteration!
    all_mcqs.append(mcq)
```

**The loop variable 'i' exists but is never used to:**
- Vary the MCQ ID: `mcq_id = f"...-{i}"`
- Select different templates: `template_variant = subtopic + f"_variant_{i}"`
- Modify the scenario: Add variations to patient demographics, presentation details

---

## Citation Title "Unknown" Issue

While investigating duplication, also found citation issue:

**Location:** `scripts/generate_day1_mcqs.py` lines 226-237

```python
"references": [
    {
        "title": citations[0]['title'] if citations else "Therapeutic Guidelines: Psychiatry",
        #        ^^^^^^^^^^^^^^^^^^^^^^^
        #        RAG returns 'title': 'Unknown' for all results
        "page": citations[0]['page'] if citations else "Section 11.5",
        "year": citations[0]['year'] if citations else 2024,
        "rag_confidence": citations[0]['confidence'] if citations else 0.0
    },
    # ... citation 2
]
```

**Issue:** RAG query returns citations with `'title': 'Unknown'`

**Root Cause:** Qdrant vector database payloads don't have 'title' field populated, or title is being lost during indexing

**Evidence:**
```json
{
  "title": "Unknown",  // ← From RAG
  "page": 1,
  "year": "2024",
  "rag_confidence": 0.762
}
```

**Impact:** All 100 MCQ entries have citations showing "Unknown" title

---

## Required Fixes

### Fix 1: ID Generation (CRITICAL)

**Current (Buggy):**
```python
mcq_id = f"PSY-DEP-{datetime.now().strftime('%Y%m%d')}-{hash(subtopic) % 1000:03d}"
```

**Fixed:**
```python
import random

# Option A: Add random component
mcq_id = f"PSY-DEP-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999):03d}"

# Option B: Use counter (preferred)
mcq_id = f"PSY-DEP-{datetime.now().strftime('%Y%m%d')}-{counter:03d}"
# Increment counter for each MCQ generated

# Option C: Use UUID
import uuid
mcq_id = f"PSY-DEP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
```

**Recommendation:** Option B (counter) - predictable, sequential, debuggable

### Fix 2: Template Variation (CRITICAL)

**Approach A: Create Multiple Templates**

```python
mcq_templates = {
    "major_depressive_disorder_diagnosis_v1": {...},  # 45yo woman, 6 weeks
    "major_depressive_disorder_diagnosis_v2": {...},  # 32yo man, 4 weeks
    "major_depressive_disorder_diagnosis_v3": {...},  # 60yo woman, severe
    "major_depressive_disorder_diagnosis_v4": {...},  # 28yo man, mild
    "major_depressive_disorder_diagnosis_v5": {...},  # 55yo woman, psychotic features
}

# Then in generation:
subtopic_base = "major_depressive_disorder_diagnosis"
for i in range(1, 6):
    subtopic_variant = f"{subtopic_base}_v{i}"
    mcq = self.generate_depression_mcq(subtopic_variant, difficulty="medium")
```

**Approach B: Programmatic Variation**

```python
def generate_depression_mcq(self, subtopic: str, difficulty: str, variant: int = 1):
    # Get base template
    base_template = mcq_templates[subtopic]

    # Apply variations based on variant number
    variations = {
        1: {"age": 45, "gender": "woman", "duration_weeks": 6},
        2: {"age": 32, "gender": "man", "duration_weeks": 4},
        3: {"age": 60, "gender": "woman", "duration_weeks": 8},
        4: {"age": 28, "gender": "man", "duration_weeks": 3},
        5: {"age": 55, "gender": "woman", "duration_weeks": 10},
    }

    var = variations[variant]
    scenario = base_template["scenario"].format(**var)
    # ... modify options, distractors based on variant
```

**Recommendation:** Approach A (multiple templates) for Week 2 immediate fix, Approach B for future scalability

### Fix 3: Citation Title Extraction

**Investigation Required:**
1. Check Qdrant indexing scripts:
   - `scripts/index_qdrant.py`
   - Verify 'title' field is being populated in payload
2. Check source data:
   - `data/chunks.json` or equivalent
   - Verify chunks have title metadata
3. Test RAG query:
   - Query Qdrant directly for sample chunks
   - Inspect payload structure

**Quick Fix (if source data missing):**
```python
citations.append({
    'title': result.payload.get('title') or result.payload.get('source') or result.payload.get('filename') or 'Medical Guideline',
    #                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #                                       Fallback chain if 'title' not available
    # ... rest of citation
})
```

---

## Generation Plan for 65 Missing MCQs

### Immediate Actions (Week 2 Day 3)

**Step 1: Fix ID generation** (5 minutes)
- Add counter to ID generation
- Test with 5 MCQs

**Step 2: Create template variants** (2-3 hours)
- For each existing subtopic, create 2-4 additional variants
- Focus on varying:
  - Patient demographics (age, gender)
  - Presentation details (duration, severity, comorbidities)
  - Distractors (incorrect options)

**Step 3: Generate 65 new unique MCQs** (1-2 hours)
- Use fixed generation scripts
- Target distribution:
  - Depression: 15 additional (to reach 20 total)
  - Anxiety/Bipolar: 14 additional (to reach 20 total)
  - Psychosis: 16 additional (to reach 25 total)
  - Suicide/MHA: 12 additional (to reach 20 total)
  - Mixed Topics: 8 additional (to reach 15 total)
  - **Total: 65 new MCQs**

**Step 4: Validate new MCQs** (30 minutes)
- Run QA-003 RAG validation on 65 new MCQs
- Check for duplicates: `len(set(all_mcq_ids)) == len(all_mcqs)`
- Verify citation diversity

---

## Long-term Prevention

### 1. Add Duplicate Detection

```python
def save_mcqs(self, mcqs: List[Dict[str, Any]], output_file: Path):
    # Check for duplicates BEFORE saving
    all_ids = [mcq['id'] for mcq in mcqs]
    unique_ids = set(all_ids)

    if len(unique_ids) != len(all_ids):
        duplicates = [id for id in all_ids if all_ids.count(id) > 1]
        raise ValueError(f"Duplicate MCQ IDs detected: {set(duplicates)}")

    # ... rest of save logic
```

### 2. Add Unit Tests

```python
def test_mcq_generation_uniqueness():
    generator = RAGIntegratedMCQGenerator()
    mcqs = generator.generate_day1_batch()

    # Test: All IDs unique
    all_ids = [mcq['id'] for mcq in mcqs]
    assert len(all_ids) == len(set(all_ids)), "MCQ IDs not unique"

    # Test: All scenarios unique
    all_scenarios = [mcq['question']['scenario'] for mcq in mcqs]
    assert len(all_scenarios) == len(set(all_scenarios)), "Scenarios not unique"
```

### 3. Template Library System

Create reusable template library with versioning:

```python
# templates/depression/mdd_diagnosis.json
{
  "v1": {"scenario": "...", "options": {...}},
  "v2": {"scenario": "...", "options": {...}},
  "v3": {"scenario": "...", "options": {...}}
}
```

Load templates dynamically and track which versions have been used.

---

## Impact Assessment

### Before Fix (Week 1)
- Total MCQ entries: 100
- Unique MCQs: 35
- Duplicates: 65
- **Duplication rate: 65%**
- **Target achievement: 35%**

### After Fix (Week 2 Target)
- Total MCQ entries: 100
- Unique MCQs: 100
- Duplicates: 0
- **Duplication rate: 0%**
- **Target achievement: 100%**

### Validation Coverage Impact

**Current (with 35 unique MCQs):**
- Tier 2 verified: 18/35 = 51.4% coverage

**After Fix (with 100 unique MCQs):**
- If 60% are Tier 2: 60 MCQs
- 90% LLM approval: 54 MCQs verified
- **Validation coverage: 54/100 = 54%**

**Not much change in percentage, but:**
- 54 verified MCQs >> 18 verified MCQs (3x more usable content)
- Achieves Week 1 100 MCQ target
- Better topic coverage (more diverse questions)

---

## Summary

### Bug Confirmed ✅
- **ID generation:** Uses hash(subtopic) → duplicate IDs
- **Template reuse:** One template per subtopic → duplicate content
- **Loop counter unused:** 'i' variable exists but never used

### Impact Quantified ✅
- **65 duplicate entries** out of 100
- **35 unique MCQs** (65% below target)
- All files affected (Day 1-5)

### Fixes Identified ✅
- **Fix 1:** Add counter/UUID to ID generation
- **Fix 2:** Create multiple templates per subtopic
- **Fix 3:** Investigate and fix citation title extraction

### Next Steps ✅
1. Implement ID generation fix
2. Create template variants for all 35 subtopics
3. Generate 65 additional unique MCQs
4. Add duplicate detection to prevent recurrence
5. Fix citation title extraction

---

**Generated:** 2026-01-25
**Priority:** HIGH (blocks Week 1 goal completion)
**Estimated Fix Time:** 3-4 hours total

