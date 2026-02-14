# QA-003 Week 2 Day 1 - Confidence Scoring Experiment Results

**Date:** 2026-01-25
**Experiment:** Test if adjusted confidence weights improve Tier 1 rate
**Hypothesis:** Increasing semantic weight and decreasing less reliable factors would boost confidence scores

---

## Changes Implemented

### Confidence Score Weights
| Factor | Week 1 Weight | Week 2 Weight | Change |
|--------|--------------|--------------|--------|
| Semantic similarity | 60% | 70% | +10% |
| Page number match | 20% | 15% | -5% |
| Source type | 10% | 10% (+ Australian boost) | 0% (+boost) |
| Recency | 10% | 5% | -5% |

### Other Improvements
- Page matching tolerance: ±2 → ±5 pages
- Australian source boost: +0.15 for eTG, RANZCP, NSW Health, Talley & O'Connor, etc.

---

## Results

### Overall Metrics Comparison

| Metric | Week 1 Baseline | Week 2 After Changes | Change |
|--------|----------------|---------------------|--------|
| **Average Confidence** | 0.773 | 0.767 | -0.006 (⬇️ WORSE) |
| **Tier 1 (≥0.90)** | 0 MCQs (0%) | 0 MCQs (0%) | No change |
| **Tier 2 (0.75-0.90)** | 58 MCQs (58%) | 58 MCQs (58%) | No change |
| **Tier 3 (<0.75)** | 42 MCQs (42%) | 42 MCQs (42%) | No change |

### Confidence Distribution Shift

**Week 1 Baseline:**
- 0.80-0.85: 54 MCQs (54%)
- 0.75-0.80: 4 MCQs (4%)
- 0.70-0.75: 32 MCQs (32%)
- <0.70: 10 MCQs (10%)

**Week 2 After Changes:**
- 0.80-0.85: 0 MCQs (0%) ⬇️ **Disappeared!**
- 0.75-0.80: 58 MCQs (58%) ⬆️ **Moved down from 0.80-0.85**
- 0.70-0.75: 36 MCQs (36%) ⬆️ **Slightly worse**
- <0.70: 6 MCQs (6%) ⬇️ **Slight improvement**

---

## Analysis: Why Did Performance DECREASE?

### Root Cause Identified
The confidence scores **decreased** because:

1. **RAG semantic scores are low (0.70-0.75 baseline)**
   - Increasing semantic weight from 60% → 70% amplified the low scores
   - We gave more weight to the weakest component!

2. **Page/recency scores were boosting overall confidence**
   - Page match score: 1.0 when pages match (or 0.5 default)
   - Recency score: 0.7-1.0 for recent sources
   - Decreasing their weight (20% → 15%, 10% → 5%) removed this boost

3. **Mathematical example:**
   - Semantic: 0.75 (low RAG score)
   - Page: 1.0 (match)
   - Source: 0.8
   - Recency: 0.9

   **Week 1 calculation:**
   0.75 × 0.60 + 1.0 × 0.20 + 0.8 × 0.10 + 0.9 × 0.10
   = 0.450 + 0.200 + 0.080 + 0.090
   = 0.820

   **Week 2 calculation:**
   0.75 × 0.70 + 1.0 × 0.15 + 0.8 × 0.10 + 0.9 × 0.05
   = 0.525 + 0.150 + 0.080 + 0.045
   = 0.800 ⬇️ **Lower!**

---

## Key Insight: The REAL Problem

**Adjusting weights won't fix this.** The fundamental issue is:

**RAG semantic scores themselves are too low (0.70-0.75 range)**

To reach Tier 1 (0.90), we need RAG semantic scores of **0.85-0.95**, not 0.70-0.75.

---

## Revised Strategy: Fix the ROOT Cause

### ❌ Failed Approach (What We Just Tried)
- Adjust confidence scoring weights
- **Result:** Made things worse by amplifying low semantic scores

### ✅ Correct Approach (What We Need to Do)
1. **Improve RAG query specificity** (HIGH PRIORITY)
   - Add ICD-10/DSM-5 codes
   - Include specific medical terminology
   - Target Australian guidelines explicitly
   - Example: "depression" → "major depressive disorder F32.9 DSM-5 criteria SSRI treatment eTG Australia"

2. **Improve RAG indexing/retrieval** (MEDIUM PRIORITY)
   - Ensure Australian guidelines (eTG, RANZCP) are properly indexed
   - Check if source_type metadata is correctly set
   - Verify embedding quality for medical terminology

3. **Regenerate content with better queries** (MEDIUM PRIORITY)
   - Regenerate 42 Tier 3 MCQs with improved RAG queries
   - Target: RAG semantic scores of 0.85+ (not 0.75)

---

## Rollback Decision

**Decision:** REVERT confidence weight changes
**Rationale:** Changes made things worse, and the real fix is improving RAG queries

**Revert to Week 1 weights:**
- Semantic: 70% → 60%
- Page: 15% → 20%
- Recency: 5% → 10%

**Keep these improvements:**
- Page tolerance: ±5 (helps with false negatives)
- Australian source boost: +0.15 (correct prioritization)

---

## Next Steps (Revised Week 2 Plan)

### Day 1 (Today) - Remaining Tasks
1. ✅ Revert confidence weights to Week 1 baseline
2. ✅ Keep page tolerance (±5) and Australian boost
3. Create improved MCQ generation templates with better RAG queries
4. Test improved queries on 5 sample MCQs

### Day 2
1. Regenerate 10 Tier 3 MCQs with improved RAG queries
2. Validate and compare semantic scores (target: 0.85+)
3. If successful, scale to all 42 Tier 3 MCQs

### Day 3-4
1. Improve RAG indexing (verify eTG/RANZCP sources)
2. Generate 20 new cardiology MCQs with improved query templates
3. Target: 50%+ Tier 1 rate on new content

### Day 5
1. Implement QA-004 LLM Verifier for Tier 2 MCQs
2. Final validation report with before/after comparison

---

## Lessons Learned

1. **Optimize the root cause, not the symptoms**
   - Adjusting weights is treating symptoms
   - Improving RAG queries fixes the root cause

2. **Test assumptions with math**
   - We assumed semantic was "most reliable"
   - But it was actually the LOWEST scoring component
   - Increasing its weight made things worse

3. **Small experiments before big rollouts**
   - Good thing we tested on existing MCQs first
   - Would have been worse to generate 100 new MCQs with bad scoring

---

**Status:** Experiment failed, but revealed the real problem
**Action:** Revert weights, focus on RAG query improvements
**Next:** Create improved MCQ generation templates
