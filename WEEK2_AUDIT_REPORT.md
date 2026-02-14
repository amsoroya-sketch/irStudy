# Week 2 Content Audit Report

**Date**: 2026-01-25
**Audit Type**: QA-003 Citation Validation
**Status**: ⚠️ **REGENERATION RECOMMENDED**

---

## Executive Summary

Week 2 content was audited using the same QA-003 validation process applied to Weeks 1 and 3. While Week 2 has **different** issues than Week 1's metadata corruption, it still requires regeneration to meet current project standards.

---

## What Was Found

### Week 2 Content Inventory

**File**: `data/mcqs/week2_day6_psychiatry_80_mcqs.json` (231 KB)

```
Total MCQs: 80
Total Citations: 160 (2 per MCQ)
File Size: 231 KB
Created: 2026-01-25 11:31
```

### QA-003 Validation Results

```
QA-003 Validation Results (2026-01-25 16:36:48):

Overall Metrics:
  Total MCQs Validated: 80
  Average Confidence: 0.720
  Auto-Approval Rate: 0.0% (Tier 1)

Tier Distribution:
  Tier 1 (>0.90 - Auto-Approve): 0 MCQs (0.0%)
  Tier 2 (0.75-0.90 - LLM Verify): 0 MCQs (0.0%)
  Tier 3 (<0.75 - Reject): 80 MCQs (100.0%)

Metadata Validation:
  Valid Citations (complete metadata): 160/160 (100.0%)
  Citations with Critical Issues: 0/160 (0.0%)
  Citations with Warnings: 20/160 (12.5%)

  ✅ ALL citations have complete metadata

Citations per MCQ:
  2 citations/MCQ: 80 MCQs (100.0%)

  ⚠️  WARNING: Some MCQs have <3 citations!
     Standard requirement: 3 citations per MCQ (Constraint 11)
```

**Validation Report**: `planning/jan-22-plan/qa_003_week2_report.json`

---

## Issue Comparison: Week 1 vs Week 2

### Week 1 Issues (Before Fix)

| Issue | Status |
|-------|--------|
| Title = "Unknown" | ❌ 212/212 (100%) |
| Missing author field | ❌ 212/212 (100%) |
| Citations per MCQ | ✅ 3 per MCQ |
| RAG-generated citations | ❌ Not used |
| Complete metadata | ❌ 0% |

**Root Cause**: RAG database missing bibliographic metadata

### Week 2 Issues (Current)

| Issue | Status |
|-------|--------|
| Title = "Unknown" | ✅ 0/160 (0%) |
| Missing author field | ✅ 0/160 (0%) - Author field present |
| Citations per MCQ | ❌ **2 per MCQ (should be 3)** |
| RAG-generated citations | ⚠️ **Manually created, not RAG** |
| Complete metadata | ✅ 100% |

**Root Cause**: Week 2 was NOT generated using the RAG system. Citations appear to be manually created rather than RAG-retrieved.

---

## Week 2 Citation Analysis

### Citation Pattern

Week 2 citations follow a **manual** pattern, not RAG-generated:

```json
{
  "title": "Therapeutic Guidelines: Psychiatry, Section 12.2 (Anxiety Disorders)",
  "year": "2024",
  "page": "Section 12.2",
  "rag_confidence": 0.7
}
```

**Evidence of Manual Creation**:
1. **Title format**: "Therapeutic Guidelines: Psychiatry, Section 12.2" (not RAG database format)
2. **Page field**: "Section 12.2" (should be a page number)
3. **Year**: "2024" (likely manually assigned)
4. **Author field**: Present but may not match RAG database

### Sample Citations (First 5)

```
1. Therapeutic Guidelines: Psychiatry, Section 12.2 (Anxiety Disorders)
2. RANZCP Clinical Practice Guidelines for Anxiety Disorders
3. Therapeutic Guidelines: Psychiatry, Section 12.2 (Anxiety Disorders)
4. RANZCP Clinical Practice Guidelines for Anxiety Disorders
5. Therapeutic Guidelines: Psychiatry, Section 12.2 (Anxiety Disorders)
```

**Pattern**: Alternating between two sources, suggesting template-based generation.

---

## Issues Requiring Regeneration

### ❌ Critical Issue 1: Missing 3rd Citation

**Current**: 2 citations per MCQ
**Required**: 3 citations per MCQ (Constraint 11)
**Impact**: 33% fewer citations than standard

**Constraint 11 Excerpt**:
> "Each MCQ must have exactly 3 RAG-retrieved citations with complete bibliographic metadata"

### ⚠️ Issue 2: Non-RAG Citations

**Current**: Citations appear manually created
**Required**: RAG-retrieved citations from validated database

**Evidence**:
- Citation titles don't match RAG database format
- Page numbers are section references (e.g., "Section 12.2"), not page numbers
- Consistent alternating pattern suggests template, not RAG retrieval

### ⚠️ Issue 3: 100% Tier 3 Classification

**Current**: 80/80 MCQs (100%) classified as Tier 3
**Expected**: Higher tier distribution with RAG-generated citations

**Note**: While Tier 3 classification doesn't invalidate the content, it suggests low RAG confidence, likely because citations were not RAG-generated.

---

## Comparison with Validated Content

### Week 1 (After Regeneration) ✅

```
MCQs: 100
Citations: 300 (3 per MCQ)
Valid Citations: 300/300 (100%)
Complete Metadata: 300/300 (100%)
RAG-generated: Yes
Zero "Unknown" Titles: ✅
```

### Week 3 (Newly Generated) ✅

```
MCQs: 500
Citations: 1,500 (3 per MCQ)
Valid Citations: 1,500/1,500 (100%)
Complete Metadata: 1,500/1,500 (100%)
RAG-generated: Yes
Zero "Unknown" Titles: ✅
```

### Week 2 (Current) ⚠️

```
MCQs: 80
Citations: 160 (2 per MCQ) ❌
Valid Citations: 160/160 (100%)
Complete Metadata: 160/160 (100%)
RAG-generated: No ⚠️
Missing 3rd Citation: 80/80 (100%) ❌
```

---

## Recommendations

### ✅ Option 1: Full Regeneration (RECOMMENDED)

**Regenerate Week 2 with validated RAG system**:
- Use same prevention system as Week 1 and Week 3
- Generate 80-100 psychiatry MCQs
- Ensure 3 citations per MCQ
- Use RAG-retrieved citations with complete metadata

**Benefits**:
- Meets Constraint 11 (3 citations per MCQ)
- Consistent with Week 1 and Week 3 standards
- RAG-validated citations
- Prevention system prevents metadata issues

**Approach**:
```bash
# STEP 1: Pre-flight validation (MANDATORY)
./scripts/pre_flight_validation.sh

# STEP 2: Generate Week 2 with incremental validation
python scripts/regenerate_week2_with_validated_citations.py

# STEP 3: Post-generation QA-003 validation
python scripts/validate_week2_mcqs_qa003.py
```

**Estimated Time**: ~5-10 minutes

### ⚠️ Option 2: Add Missing 3rd Citation

**Add 1 RAG-retrieved citation to each MCQ**:
- Keep existing 2 citations
- Query RAG for 3rd citation per MCQ
- Validate all 3 citations

**Drawbacks**:
- Existing 2 citations may not be RAG-validated
- Mixed citation sources (manual + RAG)
- Inconsistent with Week 1 and Week 3 approach

**Not Recommended**: Inconsistent citation quality

### ❌ Option 3: Keep As-Is

**Accept Week 2 with 2 citations per MCQ**

**Drawbacks**:
- Violates Constraint 11 (3 citations per MCQ)
- Inconsistent with Week 1 and Week 3
- Lower citation coverage
- Non-RAG citations

**Not Recommended**: Does not meet project standards

---

## Week 2 Regeneration Plan

### Proposed Approach: Full Regeneration

**Target**: 100 psychiatry MCQs (matching Week 1)

**Topic Distribution** (Same as Week 2 Day 6):
```
Anxiety Disorders:           20 MCQs
Substance Use Disorders:     15 MCQs
Mood Disorders:              20 MCQs
Psychotic Disorders:         15 MCQs
Trauma & Stress Disorders:   15 MCQs
Other Psychiatry:            15 MCQs
────────────────────────────────
TOTAL:                      100 MCQs
```

**Citation Standards**:
- 3 citations per MCQ (Constraint 11)
- RAG-retrieved from validated database
- Complete metadata (title, author, year, page)
- Zero tolerance for "Unknown" titles
- Incremental validation (fail-fast)

**Prevention System**:
1. ✅ Pre-flight validation (MANDATORY)
2. ✅ Incremental citation validation (fail-fast)
3. ✅ QA-003 enhanced validation
4. ✅ Zero tolerance policy

**Expected Results**:
```
MCQs: 100
Citations: 300 (3 per MCQ)
Valid Citations: 300/300 (100%)
Complete Metadata: 300/300 (100%)
Zero "Unknown" Titles: 0/300 (0%)
```

---

## Success Criteria for Week 2 Regeneration

| Criterion | Target | Current Week 2 | Expected After Regen |
|-----------|--------|----------------|----------------------|
| **MCQs Generated** | 100 | 80 | 100 ✅ |
| **Citations/MCQ** | 3 | 2 ❌ | 3 ✅ |
| **Total Citations** | 300 | 160 | 300 ✅ |
| **Valid Metadata** | 100% | 100% ✅ | 100% ✅ |
| **RAG-Generated** | Yes | No ❌ | Yes ✅ |
| **Zero "Unknown"** | 0% | 0% ✅ | 0% ✅ |
| **Pre-Flight Validation** | PASS | Not run | PASS ✅ |
| **Incremental Validation** | PASS | Not run | PASS ✅ |
| **QA-003 Final** | PASS | PARTIAL ⚠️ | PASS ✅ |

---

## Files

### Current Week 2 Files

1. **`data/mcqs/week2_day6_psychiatry_80_mcqs.json`**
   - 80 psychiatry MCQs
   - 160 citations (2 per MCQ)
   - Complete metadata
   - **⚠️  Needs regeneration**

### Week 2 Audit Files

2. **`scripts/validate_week2_mcqs_qa003.py`**
   - Week 2-specific QA-003 validator
   - Citation count analysis
   - Metadata validation

3. **`planning/jan-22-plan/qa_003_week2_report.json`**
   - QA-003 validation results
   - Detailed citation statistics
   - Issue breakdown

4. **`WEEK2_AUDIT_REPORT.md`** (this file)
   - Comprehensive audit report
   - Issue analysis
   - Regeneration recommendations

---

## Conclusion

**Week 2 Audit Summary**:

✅ **Metadata Quality**: 160/160 citations have complete metadata (100%)
❌ **Citation Count**: Only 2 citations per MCQ (should be 3 per Constraint 11)
⚠️ **RAG Usage**: Citations appear manually created, not RAG-generated
❌ **Tier Classification**: 100% Tier 3 (low RAG confidence)

**Recommendation**: ✅ **REGENERATE WEEK 2**

**Rationale**:
1. Week 2 violates Constraint 11 (3 citations per MCQ)
2. Citations are not RAG-generated (inconsistent with Weeks 1 and 3)
3. Full regeneration is faster and cleaner than partial fixes
4. Prevention system is proven effective (Week 1 + Week 3 = 1,800/1,800 valid citations)

**Next Steps**:
1. Create Week 2 regeneration script (similar to Week 1)
2. Run pre-flight validation
3. Generate 100 psychiatry MCQs with 300 RAG-validated citations
4. Run QA-003 validation (expect 100% pass)
5. Update Week 2 summary report

**Estimated Effort**: ~15 minutes (5 min setup + 10 min generation)

---

**Status**: ⚠️ AUDIT COMPLETE - REGENERATION RECOMMENDED
**Validation**: ✅ QA-003 PASSED (metadata)
**Citation Count**: ❌ 2/3 citations per MCQ (66%)

**Date**: 2026-01-25
**Audit Completion Time**: 16:36:48

---

**END OF AUDIT REPORT**
