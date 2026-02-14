# MCQ Matching Threshold Fix - 2026-02-08
**Status:** ⏳ **IN PROGRESS** - Running matching with lowered threshold

---

## Problem Identified

**Root Cause:** Tertiary matching threshold was too strict (≥3 keywords) for clinical specialties.

### Why Psychiatry Had 0% Matches:

1. **Psychiatric MCQs are CLINICAL:** Focus on symptoms (depression, anxiety, low mood, anhedonia)
2. **Psychiatric images are NEUROIMAGING:** Focus on brain pathology (MRI, CT, atrophy, lesions)
3. **Keyword mismatch:** Clinical symptoms don't overlap with neuroimaging terms
4. **Threshold too high:** MCQs extract ~2 keywords, but tertiary matching required ≥3

### Evidence:

**Sample Depression MCQ:**
- Text: "45-year-old woman with 6 weeks of low mood, anhedonia, difficulty sleeping..."
- Specialty: "Psychiatry"
- Keywords extracted: `["depression", "major depressive disorder"]` (2 keywords)

**Sample Psychiatry Image:**
- Title: "Brain MRI showing hippocampal atrophy"
- Specialty: "psychiatry"
- Keywords: `["brain", "MRI", "atrophy", "hippocampus"]` (neuroimaging terms)

**Keyword Overlap:** ZERO (clinical symptoms vs neuroimaging terms)

**Match Attempt:**
- Match 1 (Exact topic): NO - topics don't match
- Match 2 (Specialty + ≥2 keywords): NO - 0 keyword overlap
- Match 3 (≥3 keywords): NO - only 2 keywords extracted from MCQ
- **Result:** 0 matches despite both being "psychiatry"

---

## Solution Implemented

**File Modified:** `scripts/link_images_to_mcqs.py`

**Change:** Line 282 - Lowered tertiary matching threshold from ≥3 to ≥2

```python
# BEFORE:
if overlap_count >= 3:  # Required 3+ keyword overlap
    score = 30 + (overlap_count * 5)
    return score, f"keyword_overlap: {overlap_count} matches"

# AFTER:
if overlap_count >= 2:  # LOWERED to 2+ keyword overlap
    score = 30 + (overlap_count * 5)
    return score, f"keyword_overlap: {overlap_count} matches"
```

---

## Expected Impact

### Before Fix (Actual):
```
Total MCQs: 5,608
Matched: 851 (15.2%)

Specialty Breakdown:
  psychiatry: 0/1,143 (0.0%)     ❌
  paediatrics: 0/20 (0.0%)       ❌
  gastroenterology: 0/184 (0.0%) ❌
  endocrinology: 0/108 (0.0%)    ❌
  neurology: 0/84 (0.0%)         ❌
  cardiology: 319/1,703 (18.7%)  ✅
  respiratory: 267/844 (31.6%)   ✅
```

### After Fix (Expected):
```
Total MCQs: 5,608
Matched: 1,100-1,300 (19.6-23.2%)

Specialty Breakdown:
  psychiatry: 67-100/1,143 (5.9-8.7%)        ✅ Expect 50-100 matches
  paediatrics: 5-10/20 (25-50%)              ✅ Small sample
  gastroenterology: 0-20/184 (0-10.9%)       ⚠️ May still need GI imaging keywords
  endocrinology: 0-10/108 (0-9.3%)           ⚠️ May still need endo imaging keywords
  neurology: 0-20/84 (0-23.8%)               ⚠️ May still need clinical neuro keywords
  cardiology: 319-350/1,703 (18.7-20.6%)    ✅ Maintain or improve
  respiratory: 267-300/844 (31.6-35.5%)     ✅ Maintain or improve
  unknown: 265-400/1,362 (19.5-29.4%)       ✅ Better tertiary matching
```

### Key Improvements Expected:

1. **Psychiatry:** 0% → 5-10% (+50-100 MCQs)
   - Matches for MCQs with 2 psychiatric keywords
   - Still limited by clinical/imaging mismatch

2. **Unknown Specialty MCQs:** 19.5% → 25-30% (+80-140 MCQs)
   - Tertiary matching now works with 2 keywords
   - Better cross-specialty matching

3. **Paediatrics:** 0% → 25-50% (+5-10 MCQs)
   - Small sample (only 20 MCQs)
   - Should match with congenital/neonatal keywords

4. **Total Match Rate:** 15.2% → 19.6-23.2% (+250-450 MCQs)

---

## Why This Fix Works

### The Three-Tier Matching Algorithm:

**Tier 1: Exact Match (Score 100)**
- Specialty matches AND topic matches
- Most restrictive, highest quality

**Tier 2: Specialty + Keywords (Score 50-99)**
- Specialty matches AND ≥2 keyword overlap
- Good quality, requires specialty agreement

**Tier 3: Pure Keyword (Score 30-49)** ← **FIXED HERE**
- ≥2 keyword overlap (LOWERED from ≥3)
- **Why this helps:**
  - Clinical MCQs often extract only 2-3 keywords
  - Lowering to ≥2 enables matching for these MCQs
  - Still maintains quality (requires 2+ term agreement)

### Why ≥2 is Appropriate:

- **Too high (≥3):** Excludes clinical specialties with focused terminology
- **≥2 (current):** Balances coverage and quality
- **Too low (≥1):** Would create too many false positives

---

## Running Status

**Current:** ⏳ Matching algorithm running with new threshold

**Command:**
```bash
python3 scripts/link_images_to_mcqs.py 2>&1 | tee logs/mcq_matching_after_threshold_fix.log
```

**Started:** 2026-02-08 ~10:36 UTC
**Expected Duration:** 2-3 minutes (processing 5,608 MCQs × 4,537 images)

---

## Validation Plan

Once matching completes, verify:

1. **Overall improvement:**
   ```bash
   jq '.match_rate, .total_mcqs_matched' data/mcqs/mcq_image_matches.json
   ```
   - Expect: 19.6-23.2% (1,100-1,300 matches)

2. **Psychiatry unlocked:**
   ```bash
   jq '.statistics.specialty_breakdown.psychiatry' data/mcqs/mcq_image_matches.json
   ```
   - Expect: 50-100 matches (5.9-8.7%)

3. **Quality maintained:**
   ```bash
   jq '.statistics.quality_distribution' data/mcqs/mcq_image_matches.json
   ```
   - Expect: 60-70% good/excellent (lower scores due to tertiary matching)

4. **Compare logs:**
   ```bash
   diff logs/mcq_matching_after_full_keyword_expansion.log logs/mcq_matching_after_threshold_fix.log
   ```

---

## If This Fix Doesn't Work

### Alternative Approaches:

**Option A: Add Imaging Keywords for Remaining Specialties**
- Gastroenterology: bowel obstruction, IBD, endoscopy terms
- Endocrinology: thyroid nodule, pituitary adenoma
- Neurology: stroke, MS, Parkinson's clinical keywords

**Option B: Implement Specialty-Specific Thresholds**
```python
# Different thresholds for different specialty types
thresholds = {
    'imaging_heavy': 3,  # cardiology, respiratory
    'clinical_only': 2,  # psychiatry, endocrinology
    'mixed': 2,          # neurology, gastroenterology
}
```

**Option C: Semantic Matching**
- Use sentence transformers for semantic similarity
- Match MCQ text to image descriptions
- More sophisticated but requires additional library

---

## Files Modified

1. **scripts/link_images_to_mcqs.py** (line 282)
   - Changed: `if overlap_count >= 3:` → `if overlap_count >= 2:`
   - Added comment explaining the change

---

## Timeline

**10:30 UTC:** Root cause identified (threshold too strict)
**10:35 UTC:** Implemented fix (lowered threshold ≥3 → ≥2)
**10:36 UTC:** Started matching run
**10:38-10:39 UTC:** Expected completion
**10:40 UTC:** Validation and results analysis

---

**Status:** ⏳ Waiting for matching to complete...
**Next:** Analyze results and compare with expected improvements
