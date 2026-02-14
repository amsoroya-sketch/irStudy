# MCQ Regeneration & Update Tracking

**Last Updated**: 2026-01-26
**Status**: Planning Phase
**Audit Date**: 2026-01-26

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| **Total MCQ Files** | 22 | Audited |
| **Files Requiring FULL REGENERATION** | 12 | ⏳ Pending |
| **Files Requiring UPDATE ONLY** | 10 | ⏳ Pending |
| **Total MCQs Requiring FULL REGENERATION** | 1,508 | ⏳ Pending |
| **Total MCQs Requiring UPDATE** | 400 | ⏳ Pending |
| **Placeholder Patterns Detected** | 12,732 | ❌ Must Remove |

---

## Category 1: FULL REGENERATION (Placeholder → LLM Content)

**Definition**: Files contain placeholder patterns. Entire MCQ content must be regenerated with LLM.

**Requirements**:
- ❌ Remove ALL placeholder patterns (12,732 total)
- ✅ Generate clinical scenarios with patient demographics
- ✅ Generate specific question stems (not "Question about...")
- ✅ Generate detailed options (not "Option A/B/C/D")
- ✅ Generate comprehensive explanations
- ✅ Add 3 RAG-verified citations per MCQ (Constraint 11)
- ✅ Add summary field (1-2 sentences)
- ✅ Ensure 100% LLM-powered generation (Constraint 12)

### Files Requiring FULL REGENERATION

| Priority | File | MCQs | Placeholders | Status | Progress |
|----------|------|------|--------------|--------|----------|
| **1** | `missing_topics_comprehensive_mcqs.json` | 658 | 2,632 | ⏳ Pending | 0/658 (0%) |
| **2** | `week3_respiratory_200_mcqs.json` | 200 | 1,400 | ⏳ Pending | 0/200 (0%) |
| **3** | `week3_cardiology_200_mcqs.json` | 200 | 1,400 | ⏳ Pending | 0/200 (0%) |
| **4** | `week3_psychiatry_additional_100_mcqs.json` | 100 | 700 | ⏳ Pending | 0/100 (0%) |
| **5** | `week1_regenerated_100_mcqs.json` | 100 | 700 | ⏳ Pending | 0/100 (0%) |
| **6** | `week2_regenerated_100_mcqs.json` | 100 | 400 | ⏳ Pending | 0/100 (0%) |
| **7** | `missing_psychiatry_150_mcqs.json` | 150 | 900 | ⏳ Pending | 0/150 (0%) |
| **8** | `week3_respiratory_200_mcqs_with_images.json` | 200 | 1,400 | ⏳ Pending | 0/200 (0%) |
| **9** | `week3_cardiology_200_mcqs_with_images.json` | 200 | 1,400 | ⏳ Pending | 0/200 (0%) |
| **10** | `week3_psychiatry_additional_100_mcqs_with_images.json` | 100 | 700 | ⏳ Pending | 0/100 (0%) |
| **11** | `week1_regenerated_100_mcqs_with_images.json` | 100 | 700 | ⏳ Pending | 0/100 (0%) |
| **12** | `week2_regenerated_100_mcqs_with_images.json` | 100 | 400 | ⏳ Pending | 0/100 (0%) |

**Subtotal**: 2,208 MCQs requiring FULL REGENERATION

**Note**: Items 8-12 ("_with_images" files) are duplicates that will be regenerated simultaneously with items 2-6 (base files). Actual unique MCQs to regenerate: **1,508**

---

## Category 2: UPDATE ONLY (Add Summary Field)

**Definition**: Files passed validation (no placeholders). Only need to add summary field.

**Requirements**:
- ✅ Content already valid (clinical scenarios, questions, explanations)
- ✅ Citations already validated
- ✅ Australian context already present
- ➕ ADD: Summary field (1-2 sentences per MCQ)
- ➕ OPTIONAL: Enhance citations if <3 per MCQ

### Files Requiring UPDATE ONLY

| File | MCQs | Current Status | Update Required | Progress |
|------|------|----------------|-----------------|----------|
| `psychiatry_anxiety_bipolar_day2.json` | 20 | ✅ Valid | Add summaries | 0/20 (0%) |
| `psychiatry_depression_day1.json` | 20 | ✅ Valid | Add summaries | 0/20 (0%) |
| `psychiatry_final_day5.json` | 15 | ✅ Valid | Add summaries | 0/15 (0%) |
| `psychiatry_psychosis_day3.json` | 25 | ✅ Valid | Add summaries | 0/25 (0%) |
| `psychiatry_suicide_mha_day4.json` | 20 | ✅ Valid | Add summaries | 0/20 (0%) |
| `test_fixed_generation.json` | 20 | ✅ Valid | Add summaries | 0/20 (0%) |
| `week1_additional_65_mcqs.json` | 65 | ✅ Valid | Add summaries | 0/65 (0%) |
| `week1_all_100_unique_mcqs.json` | 100 | ✅ Valid | Add summaries | 0/100 (0%) |
| `week1_unique_35_mcqs.json` | 35 | ✅ Valid | Add summaries | 0/35 (0%) |
| `week2_day6_psychiatry_80_mcqs.json` | 80 | ✅ Valid | Add summaries | 0/80 (0%) |

**Subtotal**: 400 MCQs requiring UPDATE ONLY

---

## Category 3: OSCES & Study Cards (All Valid ✅)

**Status**: All OSCEs and Study Cards passed validation

| Category | Files | Items | Status |
|----------|-------|-------|--------|
| **OSCEs** | 6 | 210 | ✅ No action required |
| **Study Cards** | 5 | 140 | ✅ No action required |

**Files**:
- OSCEs: `cardiology_50_osces.json`, `respiratory_50_osces.json`, `psychiatry_40_osces.json`, `psychiatry_week1_osces.json`, `missing_topics_comprehensive_osces.json`, `missing_psychiatry_13_osces.json`
- Study Cards: `cardiology_study_cards.json`, `respiratory_study_cards.json`, `psychiatry_study_cards.json`, `missing_topics_comprehensive_cards.json`, `missing_psychiatry_13_cards.json`

---

## Detailed Regeneration Plan

### Phase 1: FULL REGENERATION (Priority 1-7)

**Script**: `scripts/regenerate_all_placeholder_mcqs_with_summaries.py`

**Files** (in execution order):
1. `missing_topics_comprehensive_mcqs.json` - 658 MCQs
2. `week3_respiratory_200_mcqs.json` - 200 MCQs
3. `week3_cardiology_200_mcqs.json` - 200 MCQs
4. `week3_psychiatry_additional_100_mcqs.json` - 100 MCQs
5. `week1_regenerated_100_mcqs.json` - 100 MCQs
6. `week2_regenerated_100_mcqs.json` - 100 MCQs
7. `missing_psychiatry_150_mcqs.json` - 150 MCQs

**Per-MCQ Process**:
1. Extract topic/specialty from placeholder MCQ
2. Query RAG for 3 relevant Australian citations
3. Generate clinical scenario with LLM (with patient demographics)
4. Generate question stem with LLM
5. Generate 4-5 options with LLM
6. Generate explanation (why_correct, why_incorrect, key_points)
7. Generate summary (1-2 sentences)
8. Validate for placeholder patterns (fail-fast)
9. Validate citations (3 required, confidence >0.70)
10. Save to output file

**Success Criteria**:
- [ ] 1,508 MCQs regenerated with LLM
- [ ] 0 placeholder patterns detected
- [ ] 4,524 citations validated (1,508 × 3)
- [ ] 100% citation validation rate
- [ ] All MCQs include summary field
- [ ] Content substance validation passes

**Estimated Time**: 2-4 hours (0.2-0.5 MCQs/second)

### Phase 2: IMAGE REGENERATION (Priority 8-12)

**Script**: `scripts/regenerate_with_images.py` (to be created)

**Files**:
1. `week3_respiratory_200_mcqs_with_images.json` - 200 MCQs
2. `week3_cardiology_200_mcqs_with_images.json` - 200 MCQs
3. `week3_psychiatry_additional_100_mcqs_with_images.json` - 100 MCQs
4. `week1_regenerated_100_mcqs_with_images.json` - 100 MCQs
5. `week2_regenerated_100_mcqs_with_images.json` - 100 MCQs

**Process**:
- Copy regenerated MCQs from Phase 1 base files
- Add image integration where appropriate (ECGs, X-rays, lab results)
- Validate image URLs/paths

**Dependencies**: Phase 1 must complete first

**Estimated Time**: 30-60 minutes (copying + image integration)

### Phase 3: UPDATE SUMMARIES (Valid Files)

**Script**: `scripts/add_summaries_to_valid_mcqs.py` (to be created)

**Files**: 10 files, 400 MCQs total

**Per-MCQ Process**:
1. Read existing MCQ (already valid)
2. Extract key learning point from explanation
3. Generate 1-2 sentence summary with LLM
4. Add "summary" field to MCQ
5. Validate summary length (50-200 characters)
6. Save updated file

**Success Criteria**:
- [ ] 400 MCQs updated with summaries
- [ ] No changes to existing content (scenarios, questions, explanations)
- [ ] All summaries 50-200 characters
- [ ] Content substance validation still passes

**Estimated Time**: 30-60 minutes (0.1-0.2 MCQs/second)

---

## Progress Tracking Template

### Current Status

**Phase 1: FULL REGENERATION**
```
Priority 1: missing_topics_comprehensive_mcqs.json
  Status: ⏳ Pending
  Progress: 0/658 MCQs (0%)
  Citations: 0/1,974 validated (0%)
  Placeholders Removed: 0/2,632 (0%)

Priority 2: week3_respiratory_200_mcqs.json
  Status: ⏳ Pending
  Progress: 0/200 MCQs (0%)
  Citations: 0/600 validated (0%)
  Placeholders Removed: 0/1,400 (0%)

... (continue for all 7 files)
```

**Phase 2: IMAGE REGENERATION**
```
Status: ⏳ Blocked (waiting for Phase 1)
Progress: 0/700 MCQs (0%)
```

**Phase 3: UPDATE SUMMARIES**
```
Status: ⏳ Pending
Progress: 0/400 MCQs (0%)
Summaries Added: 0/400 (0%)
```

---

## Overall Statistics

### Before Regeneration
- Total MCQ Files: 22
- Total MCQs: 2,958
- Valid MCQs: 750 (25%)
- MCQs with Placeholders: 2,208 (75%)
- Placeholder Patterns: 12,732
- Files with Summaries: 0 (0%)

### After Complete Regeneration (Target)
- Total MCQ Files: 22
- Total MCQs: 2,958
- Valid MCQs: 2,958 (100%) ✅
- MCQs with Placeholders: 0 (0%) ✅
- Placeholder Patterns: 0 ✅
- Files with Summaries: 22 (100%) ✅
- Total Citations: 8,874 (2,958 × 3) ✅
- Citation Validation Rate: 100% ✅

---

## Validation Checkpoints

### After Phase 1 Completion
- [ ] Run `scripts/audit_all_content_files.py` → 0 placeholder patterns
- [ ] Run `scripts/validate_content_substance.sh` on all 7 files → PASS
- [ ] Verify citations: 4,524/4,524 validated (100%)
- [ ] Verify summaries: 1,508/1,508 MCQs have summary field

### After Phase 2 Completion
- [ ] Verify image files match base files (content identical except images)
- [ ] Validate image URLs/paths accessible
- [ ] Total regenerated: 1,508 + 700 = 2,208 MCQs

### After Phase 3 Completion
- [ ] Verify all 400 valid MCQs have summary field
- [ ] Run final audit: `scripts/audit_all_content_files.py`
- [ ] Final stats: 2,958/2,958 MCQs valid (100%)

---

## Files Involved

### Scripts
- ✅ `scripts/regenerate_all_placeholder_mcqs_with_summaries.py` (Phase 1 - Created)
- ⏳ `scripts/regenerate_with_images.py` (Phase 2 - To Create)
- ⏳ `scripts/add_summaries_to_valid_mcqs.py` (Phase 3 - To Create)
- ✅ `scripts/audit_all_content_files.py` (Validation - Created)
- ✅ `scripts/validate_content_substance.sh` (Validation - Created)

### Documentation
- ✅ `REGENERATION_TRACKING.md` (This file)
- ✅ `CONTENT_AUDIT_REPORT.json` (Audit results)
- ✅ `scripts/REGENERATION_GUIDE.md` (Technical guide)
- ✅ `MCQ_REGENERATION_COMPLETE.md` (Summary)

---

## Next Steps

1. **Execute Phase 1** (FULL REGENERATION):
   ```bash
   source venv/bin/activate
   python scripts/regenerate_all_placeholder_mcqs_with_summaries.py
   ```

2. **Validate Phase 1** (after completion):
   ```bash
   python scripts/audit_all_content_files.py
   bash scripts/validate_content_substance.sh data/mcqs/missing_topics_comprehensive_mcqs.json
   ```

3. **Create Phase 2 Script** (IMAGE REGENERATION):
   - Copy regenerated content from base files
   - Add image integration

4. **Create Phase 3 Script** (UPDATE SUMMARIES):
   - Add summary field to 400 valid MCQs

5. **Final Validation**:
   ```bash
   python scripts/validate_mcqs_qa003.py
   ```

---

**Last Updated**: 2026-01-26
**Next Review**: After Phase 1 completion
