# Next Steps - Prioritized Action Plan

**Date**: 2026-05-26
**Current Status**: Integration Tests at 87.9% passing (29/33)
**Context**: Kimi completed OSCE conversion + concurrent users fixes

---

## 🎯 Current State Summary

### ✅ Completed (Today)
1. ✅ Fixed all critical integration test failures (29/33 passing)
2. ✅ Created comprehensive handover documentation (3 documents)
3. ✅ OSCE→EMR conversion tests working (3 new tests passing)
4. ✅ Concurrent users performance test fixed (sequential rapid execution)
5. ✅ Reviewed Kimi's changes - all approved

### 📊 Test Status
- **Passing**: 29/33 (87.9%)
- **Skipped**: 4/33 (12.1%) - all non-blocking
- **Failing**: 0/33 ✅
- **Regressions**: 0 ✅

---

## 🚀 Three Paths Forward

You have **3 major options** for what to continue with:

### Option A: Complete Integration Testing (PRD-MVP-004)
**Effort**: 2-3 days
**Priority**: P1 (Blocks MVP launch completeness)
**Status**: 63% complete (29/46 tests from PRD)

**Remaining Work**:
1. Cross-Module Integration Tests (12 tests) - Not yet written
2. Error Handling Tests (10 tests) - Not yet written
3. Dashboard Real-time Updates (8 tests) - Not yet written
4. Un-skip optional tests (2 tests) - Low priority

**Why Do This**:
- Complete PRD-MVP-004 to 100%
- Higher integration test coverage
- Catch cross-module bugs before production

**Why Skip This**:
- Current 87.9% pass rate is acceptable for MVP
- 4 remaining skipped tests are non-blocking
- Can add more tests post-launch

---

### Option B: Execute Flashcard Master Plan (FLASHCARD_FIX_MASTER_PLAN.md)
**Effort**: 2-3 weeks (5 phases)
**Priority**: P1 (Critical system non-functional)
**Status**: 0% complete - not started

**Major Issues to Fix**:
1. 🔴 **RAG Embeddings Broken** - Uses SHA-256 hash, not semantic
2. 🔴 **750 Static Cards Not Imported** - JSON file not in database
3. 🔴 **Frontend Not Routed** - `/study-cards` route missing
4. 🔴 **API Client Mismatch** - Wrong endpoints in frontend
5. 🟡 **54 Duplicate Cards** - Data quality issues
6. 🟡 **12% Australian Context** - Should be ≥60%

**Phase Breakdown**:
- **Phase 1**: Critical Infrastructure (RAG fix, API alignment) - 3 days
- **Phase 2**: Data Quality & Import (clean + import 750 cards) - 4 days
- **Phase 3**: Frontend Integration (routing + API client) - 3 days
- **Phase 4**: Testing & Validation (E2E, accuracy audit) - 4 days
- **Phase 5**: Australian Context Enhancement (100 new cards) - 3 days

**Why Do This**:
- Flashcard system is **completely non-functional** right now
- Critical for AMC exam preparation (core feature)
- 750 pre-made cards are ready but trapped in JSON
- RAG fix will improve all AI-generated content quality

**Why Skip This**:
- Large scope (2-3 weeks)
- Can launch MVP without flashcards (MCQ + OSCE work)
- Could be post-launch feature

---

### Option C: Address Tech Debt (From Handover Docs)
**Effort**: 5-6 hours
**Priority**: P3 (Quality improvement, not blocking)
**Status**: Warnings present, not breaking

**Tasks**:
1. **Pydantic V2 Migration** (4 hours)
   - Fix 339 deprecation warnings
   - Update `@validator` → `@field_validator`
   - Update `class Config` → `model_config = ConfigDict(...)`

2. **Datetime Modernization** (30 minutes)
   - Fix 50+ deprecation warnings
   - Replace `datetime.utcnow()` → `datetime.now(UTC)`
   - Files: `src/auth/security.py`, `src/api/v1/dashboard.py`, `tests/conftest.py`

3. **Clean Up Commented Code** (30 minutes)
   - Remove commented OSCE fixtures in conftest.py
   - Document why they were removed

**Why Do This**:
- Clean codebase, no warnings
- Prevents future Python/Pydantic breaking changes
- Professional quality code

**Why Skip This**:
- All warnings are non-breaking
- Can be done anytime
- Low ROI compared to new features

---

## 📋 My Recommendation (As PM)

### **Recommended Path: Option B - Execute Flashcard Master Plan**

**Reasoning**:
1. **High Impact**: Flashcards are a **core study method** for medical exams
2. **Currently Broken**: System is 100% non-functional (not just partially working)
3. **Ready to Execute**: Kimi created a detailed master plan with agent assignments
4. **Fixes Cascade Issues**: RAG fix will improve study cards, OSCE content, and AI responses
5. **User Value**: 750 pre-made cards + auto-generation = massive time saver for students

**Recommended Execution**:
```
Week 1 (Days 1-3): Phase 1 - Critical Infrastructure
  └─ AI-001: Fix RAG embeddings (sentence-transformers)
  └─ DEV-001: Align backend API contracts
  └─ DEV-005: Security review

Week 1 (Days 4-5): Phase 2 - Data Quality & Import (Start)
  └─ AI-005: Clean 750-card deck (dedupe, strip templates)
  └─ DEV-004: Create PostgreSQL import migration

Week 2 (Days 1-2): Phase 2 - Data Quality & Import (Finish)
  └─ MED-001: Clinical spot-check (75 cards)
  └─ DEV-004: Run import script

Week 2 (Days 3-5): Phase 3 - Frontend Integration
  └─ DEV-002: Add routing, fix API client
  └─ DEV-003: Polish components
  └─ QA-002: Write Playwright E2E tests

Week 3 (Days 1-3): Phase 4 - Testing & Validation
  └─ AI-001: RAG accuracy benchmark (50 queries)
  └─ QA-001: Clinical accuracy audit (750 cards)
  └─ QA-002: Run full E2E test suite
  └─ DEV-010: Performance testing

Week 3 (Days 4-5): Phase 5 - Australian Context Enhancement
  └─ MED-012: Generate 100 AU-specific cards
  └─ AI-005: Terminology audit
```

**Success Criteria**:
- [ ] Students can navigate to /study-cards
- [ ] 750 cards available for review
- [ ] SM-2 spaced repetition working
- [ ] Auto-generated cards have relevant RAG citations
- [ ] RAG retrieval accuracy ≥70%
- [ ] All Playwright E2E tests passing

---

## 🔄 Alternative Recommendation (If Time-Constrained)

### **Minimal MVP Path: Hybrid Approach**

If you want to **balance speed with functionality**:

**Week 1** (Focus: Get Flashcards Minimally Working)
1. Day 1-2: Execute Flashcard Phase 1 (RAG fix + API alignment)
2. Day 3: Execute Flashcard Phase 2 (import 750 cards only, skip cleaning)
3. Day 4: Execute Flashcard Phase 3 (frontend routing only)
4. Day 5: Execute Flashcard Phase 4 (minimal E2E test, 1 happy path)

**Result**: Students can use flashcards, but:
- May have some duplicate cards (54 out of 750)
- May have template artifacts in some cards
- RAG working but not benchmarked
- Minimal Australian content (12% instead of 60%)

**Post-Launch Iteration**:
- Phase 2 cleanup (deduplication, template stripping)
- Phase 4 full validation (accuracy audit)
- Phase 5 Australian enhancement (100 new cards)

---

## 📊 Decision Matrix

| Factor | Option A: Complete Integration Tests | Option B: Flashcard Master Plan | Option C: Tech Debt |
|--------|-------------------------------------|----------------------------------|---------------------|
| **User Impact** | 🟡 Medium (better QA) | 🟢 High (new feature) | 🔴 Low (internal quality) |
| **Time Investment** | 🟢 2-3 days | 🟡 2-3 weeks | 🟢 5-6 hours |
| **MVP Blocking** | 🔴 No | 🟡 Depends (flashcards important?) | 🔴 No |
| **Current Status** | 87.9% done | 0% done | N/A (warnings) |
| **Technical Risk** | 🟢 Low | 🟡 Medium (RAG changes) | 🟢 Low |
| **ROI** | 🟡 Medium | 🟢 High | 🔴 Low |

---

## 🎬 Ready-to-Execute Agent Prompts

If you choose **Option B (Flashcard Master Plan)**, I can immediately delegate:

### Task 1: Fix RAG Embeddings (AI-001 Agent)
```
Agent: AI-001 (RAG System Architect)
Priority: 🔴 Critical
Effort: 4-6 hours

Fix backend/src/ai/rag_service.py to use real semantic embeddings.

Requirements:
1. Install sentence-transformers in backend venv
2. Use 'all-mpnet-base-v2' model (768-dim to match Qdrant)
3. Cache model as class variable
4. Change collection_name from "medical_guidelines" to "medical_knowledge"
5. Create validation script: backend/scripts/validate_rag.py
6. Verify scores >0.3 for relevant medical queries

Acceptance Criteria:
- [ ] RAG retrieval scores >0.3 (not 0.01-0.07)
- [ ] Semantic consistency: "heart attack" and "myocardial infarction" retrieve similar docs
- [ ] Top-3 accuracy ≥70% on 50 medical test queries
- [ ] All existing callers of retrieve_context() still work
```

### Task 2: Import 750 Flashcards (DEV-004 Agent)
```
Agent: DEV-004 (Database Engineer)
Priority: 🔴 Critical
Effort: 6-8 hours

Create migration to import 750 flashcards from JSON to PostgreSQL.

Input: ICRP_Program_Resources/Flashcards/flashcard_data.json
Output: Alembic migration + import script

Requirements:
1. Clean cards (deduplicate, strip templates, fix empty backs)
2. Generate card_ids matching regex ^[A-Z]+-CARD-\d{4}$
3. Map 20+ deck names to 11 MedicalSpecialty enum values
4. Set SM-2 defaults (ease=2.5, interval=1, next_review=NOW)
5. Mark as public cards (user_id=NULL)
6. Idempotent script (re-run safe)

Acceptance Criteria:
- [ ] SELECT COUNT(*) FROM study_cards WHERE is_active = true >= 750
- [ ] 0 empty backs in imported cards
- [ ] 0 duplicate fronts in imported cards
- [ ] All card_ids match schema regex
- [ ] Import script logs: imported=X, skipped=Y, errors=Z
```

---

## 🤔 What Do You Want to Continue With?

**Option 1**: Execute Flashcard Master Plan (Recommended)
**Option 2**: Complete Integration Testing (PRD-MVP-004)
**Option 3**: Address Tech Debt (Pydantic V2, datetime)
**Option 4**: Something else (specify)

Let me know and I'll launch the appropriate agents!

---

**Current Time**: 2026-05-26
**Session Status**: Ready for next phase
**Blockers**: None - all options viable
