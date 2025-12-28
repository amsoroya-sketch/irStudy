# Citation Completion Summary - December 28, 2025

## Current Status

### Citation Coverage Progress

| Metric | Before | After RAG Enhancement | Improvement |
|--------|--------|----------------------|-------------|
| **Citations with exact references** | 359 (55.3%) | **546 (84.1%)** | **+187 (+28.8%)** |
| Talley with pages | 43 | 96 | +53 |
| Murtagh with pages | 306 | 411 | +105 |
| AMC with pages | 10 | 39 | +29 |
| eTG with sections | 0 | 0 | 0 |
| **Generic citations remaining** | 290 | **103** | **-187** |

### Total Coverage: **84.1%** (546/649 citations)

---

## Remaining Work: 103 Generic Citations

### Breakdown by Source

1. **Talley & O'Connor** - 55 citations without pages
2. **Murtagh's General Practice** - 19 citations without pages
3. **Therapeutic Guidelines (eTG)** - 24 citations without sections
4. **AMC Handbook** - 5 citations without pages

---

## Critical Finding: eTG Not in RAG Database

**Issue**: Therapeutic Guidelines (eTG) PDFs are NOT in the Qdrant medical_knowledge collection.

**Impact**: Cannot auto-generate section numbers for 24 eTG citations.

**Available Books in Qdrant**:
- ✅ Talley & O'Connor's Clinical Examination, 8th ed
- ✅ Murtagh's General Practice, 8th ed
- ✅ Oxford Handbook of Emergency Medicine, 5th ed
- ✅ AMC Anthology of Medical Conditions
- ✅ Churchill's Pocketbook of Differential Diagnosis
- ✅ ECG book
- ✅ On Call Principles and Protocols
- ❌ **Therapeutic Guidelines (eTG)** - NOT AVAILABLE

---

## Options for Remaining 103 Citations

### Option A: Aggressive RAG (Recommended)
**For: 74 Talley/Murtagh/AMC citations**

- Lower confidence threshold to 0.45 (from current 0.55)
- Use more context (500 chars instead of 300)
- Try multiple embedding models
- **Expected result**: Add 30-50 more page numbers
- **Remaining after**: ~25-45 citations

**Pros**: Automated, fast, scalable
**Cons**: Lower confidence scores may have some inaccuracies

### Option B: Manual Expert Review
**For: All 103 remaining citations**

- Expert manually looks up each citation in actual books
- Adds exact page numbers
- Verifies accuracy
- **Time estimate**: 2-3 hours (expert work)
- **Expected result**: 100% accuracy for all citations

**Pros**: 100% accurate, verifies correctness
**Cons**: Labor intensive, requires expert time

### Option C: Hybrid Approach (Best Balance)
**Recommended workflow**:

1. **Run aggressive RAG** (Option A) → Add 30-50 more page numbers
2. **Handle eTG specially** → See eTG strategies below
3. **Manual review remaining** → Expert reviews final 20-40 citations

**Time estimate**: 1-2 hours total
**Expected result**: 95-100% exact citation coverage

---

## eTG Citation Strategies (24 citations)

### Strategy 1: Keep Generic with Specialty (ACCEPTABLE)
**Current format**: `(Therapeutic Guidelines: Surgery - VTE Prophylaxis, 2024)`

**Justification**:
- eTG is a **digital subscription service**, not a traditional book with page numbers
- eTG uses **web-based navigation** (sections/topics, not pages)
- Including the specialty (Surgery, Cardiovascular, etc.) provides sufficient specificity
- This is **standard practice** for citing digital medical resources

**PROJECT_CONSTRAINTS.md update needed**:
```markdown
**Exception for Digital Resources:**
- eTG (Therapeutic Guidelines): Include specialty and topic when available
  - ✅ Acceptable: (Therapeutic Guidelines: Surgery - VTE Prophylaxis, 2024)
  - ✅ Acceptable: (Therapeutic Guidelines: Cardiovascular, 2024)
  - ❌ Not acceptable: (Therapeutic Guidelines, 2024) [too vague]
```

**Pros**:
- Already compliant
- Matches standard medical citation practice
- No additional work needed

**Cons**:
- Not page-specific
- Readers need eTG subscription to verify

### Strategy 2: Add eTG PDFs to Qdrant (FUTURE ENHANCEMENT)
**Process**:
1. Obtain eTG PDFs (requires eTG subscription + PDF export)
2. Chunk PDFs into sections
3. Add to Qdrant medical_knowledge collection
4. Re-run RAG to extract section numbers
5. Update citations with section numbers

**Time estimate**: 4-6 hours
**Expected result**: Section numbers for all 24 eTG citations

**Pros**:
- Exact section references
- Reusable for future citations

**Cons**:
- Requires eTG subscription
- May have licensing restrictions on PDF use
- Time intensive setup

### Strategy 3: Replace eTG with Book Citations (NOT RECOMMENDED)
**Process**: Re-write claims to reference Talley/Murtagh instead of eTG

**Example**:
- Before: `LMWH 40mg SC daily (Therapeutic Guidelines: Surgery, 2024)`
- After: `LMWH 40mg SC daily for VTE prophylaxis (Murtagh's GP, 8th ed, p.892)`

**Pros**: Uses available RAG sources

**Cons**:
- Loses Australian eTG authority (gold standard in Australia)
- May not find equivalent claim in general practice books
- Not recommended - eTG is more authoritative for treatment protocols

---

## Recommended Action Plan

### Phase 1: Aggressive RAG on Talley/Murtagh/AMC (30 min)
```bash
python3 add_remaining_page_numbers_aggressive.py
# Threshold: 0.45
# Context: 500 chars
# Expected: +30-50 page numbers
```

### Phase 2: eTG Decision (5 min)
**Decision needed**:
- [ ] Accept current eTG format as compliant (with specialty)?
- [ ] OR pursue Strategy 2 (add eTG to Qdrant)?

**Recommendation**: Accept current eTG format with specialty as compliant.

### Phase 3: Manual Review Remaining (1-2 hours)
- Expert reviews remaining 20-40 low-confidence citations
- Manually adds page numbers from physical books
- Documents any citations that can't be verified

### Phase 4: Validation & Report (15 min)
```bash
python3 validate_exact_citations.py
# Generates final report
# Logs all confidence scores
```

---

## Expected Final Outcome

| Metric | Current | After Phase 1 | After Phase 3 | Target |
|--------|---------|---------------|---------------|--------|
| Exact references | 546 (84.1%) | ~590 (91%) | ~625 (96%) | 95%+ |
| Generic citations | 103 | ~60 | ~24 (eTG only) | <5% |
| eTG with specialty | 24 | 24 | 24 | Accepted |
| Manual review needed | 103 | ~35 | 0 | 0 |

**Final citation compliance**: 96% with exact page numbers + 4% eTG with specialty = **100% compliant**

---

## Time Estimate Summary

| Phase | Time | Who |
|-------|------|-----|
| Aggressive RAG | 30 min | Automated |
| eTG decision | 5 min | User/PM |
| Manual review | 1-2 hours | Expert |
| Validation | 15 min | Automated |
| **TOTAL** | **2-3 hours** | |

---

## Next Steps

**Awaiting user decision on**:
1. Run aggressive RAG (threshold 0.45)?
2. Accept eTG specialty format as compliant?
3. Proceed with manual expert review for final ~35 citations?

---

**Report Generated**: December 28, 2025, 12:20 PM
**Status**: 84.1% citation coverage achieved, 103 citations remaining
