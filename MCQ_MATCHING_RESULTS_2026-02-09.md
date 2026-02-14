# MCQ Matching Results - Keywords Enhancement

**Date:** 2026-02-09
**Keywords Added:** 43 patterns (Neurology: 15, Gastroenterology: 16, Endocrinology: 12)
**Status:** ⚠️ PARTIAL SUCCESS - Needs Investigation

---

## Executive Summary

**Overall Improvement:** ✅ **+464 matches (+10.5%)**
- Before: 975/5,608 (15.2%)
- After: 1,439/5,608 (25.7%)

**However:** Keywords didn't improve neurology/GI/endo as expected ⚠️

---

## Detailed Results

### Overall Statistics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total MCQs | 5,608 | 5,608 | - |
| MCQs Matched | 975 | 1,439 | **+464** ✅ |
| Match Rate | 15.2% | 25.7% | **+10.5%** ✅ |

### Match Quality Distribution

| Quality | Count | Percentage |
|---------|-------|------------|
| Excellent (≥80) | 213 | 14.8% |
| Good (60-79) | 373 | 25.9% |
| Fair (40-59) | 853 | 59.3% |

### Specialty Breakdown

| Specialty | Matched/Total | Match Rate | Change |
|-----------|---------------|------------|--------|
| **unknown** | 853/1,362 | 62.6% | ⚠️ HIGH |
| **respiratory** | 267/844 | 31.6% | No change |
| **cardiology** | 319/1,703 | 18.7% | No change |
| **psychiatry** | 0/1,143 | 0.0% | No change |
| **gastroenterology** | 0/184 | 0.0% | ❌ Expected improvement |
| **general medicine** | 0/156 | 0.0% | - |
| **endocrinology** | 0/108 | 0.0% | ❌ Expected improvement |
| **neurology** | 0/84 | 0.0% | ❌ Expected improvement |
| **paediatrics** | 0/20 | 0.0% | No change |
| **hematology** | 0/3 | 0.0% | - |
| **emergency_medicine** | 0/1 | 0.0% | - |

---

## Key Finding: The "Unknown" Mystery

**Problem:**
- 853 matches fell into "unknown" specialty (62.6% match rate!)
- Expected neurology/GI/endo specialties show 0 matches
- Keywords ARE working (overall +464 matches) but categorized wrong

**Investigation Needed:**
1. Why are matches categorized as "unknown"?
2. Are neurology/GI/endo MCQs actually in those 853 "unknown" matches?
3. Is there a specialty normalization bug in statistics aggregation?

---

## Files Processed

**Total:** 41 MCQ files, 5,608 MCQs

**High Match Files:**
- `week3_respiratory_200_mcqs_backup_all_batches_20260131_142651.json`: 126/200 (63.0%)
- `week3_respiratory_200_mcqs_backup_all_batches_20260131_112726.json`: 116/200 (58.0%)
- `week3_respiratory_200_mcqs_backup_all_batches_20260131_104804.json`: 107/200 (53.5%)
- `week3_respiratory_200_mcqs.json`: 103/200 (51.5%)
- `week3_cardiology_200_mcqs_backup_batch8_FINAL_20260129_123426.json`: 84/200 (42.0%)

**Low/Zero Match Files:**
- All psychiatry files: 0% (as expected - content mismatch)
- `missing_topics_comprehensive_mcqs.json`: 24/658 (3.6%) ⚠️
  - Contains: Endocrinology, Gastroenterology, Neurology, General Medicine
  - Should have much higher match rate with new keywords

**Specialty Distribution in Files:**
From `missing_topics_comprehensive_mcqs.json`:
- Cardiology
- **Endocrinology** ← Keywords added, but 0% match reported
- **Gastroenterology** ← Keywords added, but 0% match reported
- General Medicine
- **Neurology** ← Keywords added, but 0% match reported

---

## Comparison: Before vs After

### Before Keywords (Feb 8, 15.2%)
```
Total: 975 matches
- Respiratory: 267 (31.6%)
- Cardiology: 319 (18.7%)
- Psychiatry: 67 (5.9%)
- All others: 0
```

### After Keywords (Feb 9, 25.7%)
```
Total: 1,439 matches
- Unknown: 853 (62.6%) ← +853 NEW
- Respiratory: 267 (31.6%) ← No change
- Cardiology: 319 (18.7%) ← No change
- Psychiatry: 0 (0.0%) ← LOST 67 matches?!
- All others: 0
```

---

## Anomalies Detected

### 1. Psychiatry Regression ⚠️
- Before: 67/1,143 (5.9%)
- After: 0/1,143 (0.0%)
- **Lost 67 matches** - Why?

### 2. "Unknown" Explosion ⚠️
- Before: ~265 unknown matches
- After: 853 unknown matches
- **+588 matches went to "unknown"**

### 3. Expected Specialties at 0% ⚠️
- Neurology: 0/84 (expected 40-60%)
- Gastroenterology: 0/184 (expected 30-50%)
- Endocrinology: 0/108 (expected 25-40%)

---

## Hypothesis: Statistics Aggregation Bug

**Theory:**
The matching IS working (overall +464 matches proves it), but statistics are being aggregated incorrectly.

**Evidence:**
1. Total matches increased from 975 to 1,439 (+464)
2. But known specialties (cardiology, respiratory) didn't change
3. All new matches went to "unknown"
4. Psychiatry lost all matches

**Possible Causes:**
1. Specialty normalization inconsistency between matching and statistics
2. Bug in `process_mcq_file()` statistics aggregation (line ~328-370)
3. Different specialty field extraction in statistics vs matching

---

## Next Steps Required

### Immediate Investigation (30 min)

**1. Check actual match data:**
```bash
# Sample "unknown" matches to see their actual specialty
jq -r '.matches | to_entries[] | select(.value.specialty == "unknown") |
  {mcq_id: .key, specialty: .value.mcq.specialty, topic: .value.mcq.topic,
   match_count: (.value.matches | length)}' data/mcqs/mcq_image_matches.json | head -20
```

**2. Verify neurology/GI/endo MCQs exist:**
```bash
# Count MCQs by specialty in source files
jq -r '.mcqs[].specialty' data/mcqs/*.json | sort | uniq -c | sort -rn
```

**3. Debug statistics aggregation:**
- Add debug logging to `process_mcq_file()` line ~328
- Print specialty before/after normalization
- Check why matches go to "unknown"

### Fix Strategy (1 hour)

**Option A: Fix Statistics Aggregation**
- Debug `process_all_mcqs()` method
- Ensure consistent specialty normalization
- Re-run matching after fix

**Option B: Accept and Document**
- If "unknown" contains neurology/GI/endo matches, relabel them
- Update statistics post-processing
- Document as known limitation

**Option C: Investigate and Report**
- Create detailed bug report
- Test with sample MCQs
- Fix root cause

---

## Success Criteria Check

### ✅ Achieved
- Overall match rate improved: 15.2% → 25.7% (+10.5%)
- Keywords successfully added (43 patterns)
- Matching algorithm executed without errors
- 464 new matches created

### ❌ Not Achieved
- Neurology: 0% (expected 40-60%)
- Gastroenterology: 0% (expected 30-50%)
- Endocrinology: 0% (expected 25-40%)
- Psychiatry regressed from 5.9% to 0%

### ⚠️ Unclear
- Are the 853 "unknown" matches actually neurology/GI/endo?
- Is this a categorization bug or real mismatch?

---

## Files Generated

- ✅ `data/mcqs/mcq_image_matches.json` (updated)
- ✅ `logs/mcq_matching_with_neuro_gi_endo_keywords.log` (complete)
- ✅ `MCQ_MATCHING_RESULTS_2026-02-09.md` (this file)

---

## Recommendation

**DO NOT** proceed with database integration or manual curation until we understand why:
1. 853 matches are categorized as "unknown"
2. Neurology/GI/endo show 0% despite keywords
3. Psychiatry lost all 67 matches

**Priority:** Investigate "unknown" category to verify if it contains the expected specialty matches.

---

**Status:** ⚠️ NEEDS INVESTIGATION
**Next Action:** Sample "unknown" matches to verify actual specialty distribution
**Time Required:** 30-60 minutes for full diagnosis
