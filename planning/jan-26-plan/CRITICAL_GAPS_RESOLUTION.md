# Critical Gaps Resolution Plan

**Date**: 2026-01-26
**Status**: 🔴 **BLOCKING ISSUES** - Must fix before Day 1 execution
**Priority**: P0 (Highest)

---

## 🚨 Critical Gap #1: RAG Integration (BLOCKING Day 1)

### Problem
```python
# Current QdrantClient returns empty results
def search(...):
    return []  # ❌ Always returns empty!
```

**Impact**: Day 1 will generate **0 MCQs** because:
- RAG citation fetching fails (returns 0 results)
- Script requires exactly 3 citations (Constraint 11)
- Without citations, MCQ generation is skipped

### Root Cause
Qdrant has 9,950 vectors in collection `medical_knowledge`, but our client doesn't:
1. Generate embeddings for query text
2. Perform actual vector search
3. Return scored results

### Solution: Implement Minimal Working RAG

**File to update**: `src/rag/qdrant_client.py`

**Required changes**:
```python
from sentence_transformers import SentenceTransformer

class QdrantClient:
    def __init__(self, host="localhost", port=6333):
        self.base_url = f"http://{host}:{port}"
        # Load embedding model (same as used for indexing)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, collection_name, query_text, limit=5, filter=None):
        # 1. Generate embedding for query
        query_embedding = self.model.encode(query_text).tolist()

        # 2. Search Qdrant
        url = f"{self.base_url}/collections/{collection_name}/points/search"
        payload = {
            "vector": query_embedding,
            "limit": limit,
            "with_payload": True,
            "score_threshold": 0.5  # Minimum similarity
        }

        if filter:
            payload["filter"] = filter

        response = requests.post(url, json=payload)
        response.raise_for_status()

        # 3. Return SearchResult objects
        results = response.json().get("result", [])
        return [
            SearchResult(
                score=hit["score"],
                payload=hit["payload"]
            )
            for hit in results
        ]
```

**Dependencies needed**:
```bash
pip install sentence-transformers
```

**Estimated time**: 10 minutes

---

## 🚨 Critical Gap #2: OSCE Methodology Integration (Week 4 blocker)

### Problem
Existing 210 OSCEs missing:
- ❌ `summary` field
- ❌ `differential_diagnosis` (Principle 1)
- ❌ `examination_framework` (Principle 2)
- ❌ `time_allocation` (Principle 3)
- ❌ `australian_context` (Principle 4)

### Solution: Update All Planning Documents

**Files to update**:
1. `PER_DAY_EXECUTION_PLAN.md` - Change "add summaries (2-3 hours)" to "OSCE methodology integration (3 days)"
2. `FINAL_EXECUTION_PLAN_APPROVED.md` - Add OSCE enhancement details
3. `COMPLETE_SCOPE_PLAN.md` - Document full OSCE structure
4. Create `scripts-jan-26/enhance_osces_with_methodology.py`
5. Create `scripts/validate_osce_methodology_compliance.py`

**Estimated time**: 30 minutes planning + 2 hours script creation

---

## ✅ Immediate Action Plan

### Step 1: Fix RAG Integration (15 min)
1. Install sentence-transformers
2. Update `src/rag/qdrant_client.py` with working search
3. Test with sample query
4. Verify returns results with >0.70 confidence

### Step 2: Test Day 1 Script (5 min)
1. Run Day 1 script with first topic (STEMI)
2. Generate 3-5 MCQs as proof-of-concept
3. Validate output structure
4. Confirm no placeholder patterns

### Step 3: Update Planning Docs (30 min)
1. Update `PER_DAY_EXECUTION_PLAN.md` Week 4 section
2. Add OSCE methodology requirements to all relevant docs
3. Create OSCE enhancement script template
4. Update HTML conversion plan to include new OSCE fields

### Step 4: Document Decisions (10 min)
1. Update `README.md` in jan-26-plan folder
2. Mark OSCE methodology integration as Phase 4
3. Update timeline estimate (add 3 days for OSCE work)

**Total time**: ~60 minutes to unblock Day 1 execution

---

## 📋 Resolution Checklist

### RAG Integration: ✅ COMPLETE (2026-01-26)
- [x] Install sentence-transformers package (already in venv)
- [x] Update QdrantClient with embedding model (PubMedBERT 768-dim)
- [x] Implement vector search (was working, just wrong model)
- [x] Test query returns results (5 results, 95.63% avg confidence)
- [x] Verify confidence scores >0.70 (all citations >95%)
- [x] Run proof-of-concept test (PASSED - see RAG_INTEGRATION_VERIFIED.md)

### OSCE Methodology:
- [ ] Create OSCE_METHODOLOGY_INTEGRATION.md (✅ DONE)
- [ ] Update PER_DAY_EXECUTION_PLAN.md Week 4 section
- [ ] Update FINAL_EXECUTION_PLAN_APPROVED.md
- [ ] Create enhance_osces_with_methodology.py template
- [ ] Create validate_osce_methodology_compliance.py
- [ ] Update HTML_CONVERSION_PLAN.md for new OSCE fields

### Documentation:
- [ ] Update jan-26-plan README.md
- [ ] Add to LESSONS_LEARNED_AND_MISTAKES.md
- [ ] Update project timeline (add 3 days for OSCEs)

---

## 🎯 Success Criteria

**RAG Fixed When:**
- QdrantClient returns 3+ results for "STEMI troponin ECG"
- Results have `score` ≥ 0.70
- Results have `payload` with content, source, page
- Day 1 script generates MCQs successfully

**OSCE Methodology Integrated When:**
- All planning docs reference 9 principles
- Enhancement scripts created
- Validation checks all principles
- Timeline reflects 3-day OSCE work (not 2-3 hours)

---

## ⏱️ Updated Timeline Impact

**Original estimate**:
- Week 4 Day 12: OSCE summaries (2-3 hours)

**Corrected estimate**:
- Week 4 Days 19-21: OSCE methodology integration (24 hours total)
  - Day 19: Batch 1 - 70 OSCEs
  - Day 20: Batch 2 - 70 OSCEs
  - Day 21: Batch 3 - 70 OSCEs

**Project completion**: Extended by 2.5 days

---

## 🚀 Next Steps

**Immediate (next 60 min)**:
1. Fix RAG integration
2. Test Day 1 generation (3-5 MCQs)
3. Update planning docs

**After RAG fix confirmed**:
4. Continue with full Day 1 execution (145 MCQs)
5. Proceed with Week 1 as planned

**Week 4 prep**:
6. Create OSCE enhancement scripts
7. Test on 1 sample OSCE
8. Prepare for 3-day OSCE integration

---

**Document Status**: 🔴 Action Required - Two P0 blockers identified
**Owner**: Development team
**ETA to resolve**: 60 minutes for RAG + Day 1 testing
**Date**: 2026-01-26
