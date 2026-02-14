# Phase 3 Migration Conflict - Blocking Issue

**Date:** 2026-02-07
**Status:** ⚠️ BLOCKED - Multiple migration heads detected
**Phase:** Phase 3 of 6 (Database Migration Execution)

---

## Issue Summary

**Problem:** Alembic reports multiple head revisions, preventing migrations from running

**Error Message:**
```
ERROR [alembic.util.messaging] Multiple head revisions are present for given argument 'head'; please specify a specific target revision, '<branchname>@head' to narrow to a specific head, or 'heads' for all heads
```

**Root Cause:** Two migration files both set `down_revision = '001'`:
1. `20260204_1012_4dee6b483097_add_tags_to_osces.py` - Revision 4dee6b483097
2. `20260207_0805_002_add_study_cards_table.py` - Revision 002

This creates a branching migration tree instead of a linear chain:

```
001 (initial schema)
 ├─> 4dee6b483097 (OSCE tags)
 └─> 002 (Study Cards)
```

**Expected linear chain:**
```
001 → 4dee6b483097 → 002
```

---

## Analysis

### Migration Files

**File 1: OSCE Tags**
- Path: `/home/dev/Development/irStudy/backend/alembic/versions/20260204_1012_4dee6b483097_add_tags_to_osces.py`
- Revision: `4dee6b483097`
- Down revision: `001`
- Created: 2026-02-04 (3 days ago)
- Purpose: Add tags column to OSCEs table

**File 2: Study Cards**
- Path: `/home/dev/Development/irStudy/backend/alembic/versions/20260207_0805_002_add_study_cards_table.py`
- Revision: `002`
- Down revision: `001`
- Created: 2026-02-07 (THIS session - today)
- Purpose: Create study_cards table with SM-2 algorithm support

### Why This Happened

1. OSCE tags migration was created on Feb 4 (other session/earlier work)
2. Study Cards migration was created today (THIS session)
3. Study Cards migration was auto-generated with `down_revision = '001'` (default behavior)
4. Alembic didn't detect the existing migration chain (4dee6b483097)
5. Result: Two migrations both claiming to follow '001'

---

## Fix Required

**Option A: Update Study Cards Migration** (RECOMMENDED - preserves history)
1. Edit `20260207_0805_002_add_study_cards_table.py`
2. Change `down_revision = '001'` to `down_revision = '4dee6b483097'`
3. This makes Study Cards depend on OSCE tags migration
4. Resulting chain: 001 → 4dee6b483097 → 002

**Option B: Merge Migrations** (NOT recommended - loses granularity)
1. Delete Study Cards migration
2. Create new migration that depends on 4dee6b483097
3. Re-generate Study Cards table creation

**Option C: Rebase Migration History** (NOT recommended - dangerous)
1. Delete all migrations
2. Re-create from scratch
3. Risk: May lose migration history if already applied elsewhere

---

## Recommendation

**Use Option A** (Update Study Cards Migration):
- Simplest fix (1-line change)
- Preserves all migration history
- Safe (no database changes needed, just file edit)
- Fast (30 seconds)

---

## Implementation Steps (Option A)

1. **Edit migration file:**
   ```bash
   File: backend/alembic/versions/20260207_0805_002_add_study_cards_table.py
   
   Change line 24 from:
   down_revision: Union[str, None] = "001"
   
   To:
   down_revision: Union[str, None] = "4dee6b483097"
   ```

2. **Verify fix:**
   ```bash
   cd backend
   source ../venv/bin/activate
   set -a && source .env && set +a
   alembic heads  # Should show only ONE head: 002
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head  # Should apply all 3 migrations in order
   ```

4. **Verify database:**
   ```bash
   docker exec amc-postgres-dev psql -U amc_user -d irstudy_medical -c "\dt"
   # Expected tables: users, mcqs, osces, study_cards, mcq_attempts, user_progress, user_favorite_mcqs, user_favorite_osces, alembic_version
   ```

---

## Impact on Execution Plan

**Phase 1:** ✅ COMPLETE (Database created)
**Phase 2:** ✅ COMPLETE (Backend config verified)
**Phase 3:** ⚠️ BLOCKED (Migration conflict - FIX REQUIRED)
**Phase 4:** ⏸️ WAITING (Blocked by Phase 3)
**Phase 5:** ⏸️ WAITING (Blocked by Phase 3)
**Phase 6:** ⏸️ WAITING (Blocked by Phase 3)

**Estimated Delay:** 5 minutes (edit 1 line, re-run migrations)

---

## Zero-Error Policy Compliance

**Status:** ✅ POLICY FOLLOWED
- Issue detected BEFORE database modifications
- No data corruption risk
- No production impact (database is empty)
- Fix is simple and safe
- Validation steps defined

**Root Cause Prevention:**
- When creating future migrations, ALWAYS check `alembic heads` first
- If multiple heads exist, manually set `down_revision` to latest revision
- Update migration creation checklist to include this step

---

## Next Actions

**PM Decision Required:**
1. Approve Option A fix (recommended)
2. Execute fix (PM can do directly - 1-line edit)
3. Resume Phase 3 (run migrations)
4. Proceed to Phase 4 (data import)

**Alternative:**
- Delegate to database-expert agent if PM prefers review before edit

---

**Awaiting PM approval to proceed with Option A fix.**
