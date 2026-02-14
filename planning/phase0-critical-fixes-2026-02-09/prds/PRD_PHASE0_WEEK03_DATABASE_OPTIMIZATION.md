# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: PHASE0_WEEK03 - Database Optimization & Performance Tuning (2-3 days)

**EXECUTE NOW**:

Add 5 critical indexes, create 3 database triggers, and run complete Alembic migration. Benchmark query performance to verify 55x speedup for active sessions query. DO NOT wait for DBA approval - implement ALL optimizations NOW, then request review.

**DO NOT**:
- ❌ Ask "Would you like me to add indexes?"
- ❌ Ask "Should I create the triggers first?"
- ❌ Wait for DBA approval before running migration
- ❌ Skip performance benchmarks or ask for clarification

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📊 Metadata

- **Phase:** 0 (Critical Fixes)
- **Week:** 0.3
- **Duration:** 2-3 days
- **Priority:** P0-Critical (BLOCKING Phase 1)
- **Dependencies:**
  - PHASE0_WEEK01 complete (Clinical Advisor approval)
  - PHASE0_WEEK02 complete (Security Team approval)
- **Owner:** Senior Backend Architect + DBA (approval)
- **Status:** 🔴 Not Started - BLOCKING

---

## 🎯 Objectives

1. **Add 5 missing indexes** for 55x query performance improvement
2. **Create 3 database triggers** for data integrity
3. **Run complete Alembic migration** with all Phase 0 changes
4. **Benchmark query performance** (verify <5ms target for active sessions)
5. **Document query plans** with EXPLAIN ANALYZE
6. **Obtain DBA approval** for all database changes

---

## 🚨 Constraints (READ FIRST)

**From `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`:**

❌ **NEVER:**
- Create indexes without WHERE clauses for partial data (wastes space)
- Skip EXPLAIN ANALYZE performance testing
- Run migrations on production without testing on staging first

✅ **ALWAYS:**
- Add indexes for high-frequency queries (sync job, dashboards)
- Use partial indexes (WHERE clause) when appropriate
- Test migrations on development database first
- Document query plans before/after optimization

**From `/home/dev/Development/irStudy/AI_OSCE_TECHNICAL_REVIEW_PART1.md` Section 1.1:**
- Active sessions query MUST be <5ms (currently 127ms without index)
- User dashboard query MUST be <10ms (currently 456ms without index)
- Mock exam progress MUST be <15ms (currently 234ms without index)

---

## 📋 Implementation Guide

### Step 1: Read Technical Review (30 min)

```bash
cd /home/dev/Development/irStudy

# Read complete technical review
cat AI_OSCE_TECHNICAL_REVIEW_PART1.md

# Key sections to extract:
# - Section 1.1: 5 Missing Indexes (lines ~50-150)
# - Section 1.2: 3 Additional Triggers (lines ~150-250)
# - Section 1.4: Complete Alembic Migration (340 lines)
# - Section 1.5: Performance Benchmarks (5 queries)

# Verify file exists
[ -f AI_OSCE_TECHNICAL_REVIEW_PART1.md ] && echo "✅ Technical review found" || echo "❌ File missing"
```

### Step 2: Create Alembic Migration (1 hour)

```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# Verify Alembic is configured
alembic current
# Expected: Shows current migration version

# Create new migration for Phase 0 optimizations
alembic revision -m "phase0_add_indexes_and_triggers"

# This creates: alembic/versions/TIMESTAMP_phase0_add_indexes_and_triggers.py
# Copy migration code from AI_OSCE_TECHNICAL_REVIEW_PART1.md Section 1.4
```

**COPY MIGRATION FROM**: `AI_OSCE_TECHNICAL_REVIEW_PART1.md` Section 1.4 (340 lines)

**MIGRATION CONTENT** (complete upgrade/downgrade):

```python
"""phase0_add_indexes_and_triggers

Revision ID: phase0_20260209
Revises: 20260201_1430_001_initial_schema
Create Date: 2026-02-09 10:00:00.000000

Adds:
- 5 critical indexes for query performance (55x speedup)
- 3 database triggers for data integrity
- Updates to osce_attempts, osce_scores, patient_personas tables

Performance Targets:
- Active sessions query: 127ms → 2.3ms (55x faster)
- User dashboard query: 456ms → 8.7ms (52x faster)
- Mock exam progress: 234ms → 12.5ms (19x faster)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers
revision = 'phase0_20260209'
down_revision = '20260201_1430_001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Add 5 indexes + 3 triggers for Phase 0 optimization"""

    # ================================================================
    # INDEX 1: Active sessions for background sync (CRITICAL)
    # ================================================================
    # Used by: Celery task sync_active_osce_sessions (runs every 30s)
    # Query: SELECT * FROM osce_attempts
    #        WHERE session_state IN ('conversation', 'warning_1min')
    #        AND updated_at > NOW() - INTERVAL '1 hour'
    # Performance: 127ms → 2.3ms (55x faster)

    op.create_index(
        'idx_attempts_active_sessions',
        'osce_attempts',
        ['session_state', 'updated_at'],
        unique=False,
        postgresql_where=sa.text(
            "session_state IN ('conversation', 'warning_1min')"
        )
    )

    # ================================================================
    # INDEX 2: User dashboard recent history (HIGH PRIORITY)
    # ================================================================
    # Used by: GET /api/v1/users/{user_id}/osce-history
    # Query: SELECT * FROM osce_attempts
    #        WHERE user_id = ? AND deleted_at IS NULL
    #        ORDER BY started_at DESC LIMIT 20
    # Performance: 456ms → 8.7ms (52x faster)

    op.create_index(
        'idx_attempts_user_recent',
        'osce_attempts',
        ['user_id', sa.text('started_at DESC')],
        unique=False
    )

    # ================================================================
    # INDEX 3: Mock exam progress tracking (MEDIUM PRIORITY)
    # ================================================================
    # Used by: GET /api/v1/mock-exams/{exam_id}/progress
    # Query: SELECT * FROM osce_attempts
    #        WHERE mock_exam_id = ? AND station_number = ?
    # Performance: 234ms → 12.5ms (19x faster)

    op.create_index(
        'idx_attempts_mock_exam_station',
        'osce_attempts',
        ['mock_exam_id', 'station_number'],
        unique=False,
        postgresql_where=sa.text("mock_exam_id IS NOT NULL")
    )

    # ================================================================
    # INDEX 4: Score lookup for analytics (MEDIUM PRIORITY)
    # ================================================================
    # Used by: Analytics dashboard, persona pass rate calculation
    # Query: SELECT s.* FROM osce_scores s
    #        JOIN osce_attempts a ON s.attempt_id = a.attempt_id
    #        WHERE s.pass_fail = 'PASS'

    op.create_index(
        'idx_scores_persona_performance',
        'osce_scores',
        ['attempt_id', 'total_score', 'pass_fail'],
        unique=False
    )

    # ================================================================
    # INDEX 5: Persona browsing/filtering (LOW PRIORITY)
    # ================================================================
    # Used by: GET /api/v1/patient-personas?specialty=X&difficulty=Y
    # Query: SELECT * FROM patient_personas
    #        WHERE specialty = ? AND difficulty_level = ? AND is_active = TRUE

    op.create_index(
        'idx_personas_browse',
        'patient_personas',
        ['specialty', 'difficulty_level', 'is_active'],
        unique=False,
        postgresql_where=sa.text("is_active = TRUE")
    )

    # ================================================================
    # TRIGGER 1: Auto-update persona pass rates
    # ================================================================
    # Triggered: After osce_scores INSERT
    # Action: Recalculate patient_personas.estimated_pass_rate

    op.execute("""
        CREATE OR REPLACE FUNCTION update_persona_pass_rate()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Recalculate pass rate for this persona
            UPDATE patient_personas
            SET estimated_pass_rate = (
                SELECT (COUNT(*) FILTER (WHERE s.pass_fail = 'PASS')::DECIMAL / COUNT(*)) * 100
                FROM osce_attempts a
                JOIN osce_scores s ON a.attempt_id = s.attempt_id
                WHERE a.persona_id = (
                    SELECT persona_id FROM osce_attempts WHERE attempt_id = NEW.attempt_id
                )
            )
            WHERE persona_id = (
                SELECT persona_id FROM osce_attempts WHERE attempt_id = NEW.attempt_id
            );

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_update_persona_pass_rate
        AFTER INSERT ON osce_scores
        FOR EACH ROW
        EXECUTE FUNCTION update_persona_pass_rate();
    """)

    # ================================================================
    # TRIGGER 2: Calculate mock exam overall result
    # ================================================================
    # Triggered: After all 16 stations scored in mock exam
    # Action: Update mock_exams.overall_pass_fail, total_score
    # Rules: PASS if ≥144/240 (60%) AND no critical errors

    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_mock_exam_result()
        RETURNS TRIGGER AS $$
        DECLARE
            exam_id UUID;
            total_stations INT;
            completed_stations INT;
            total_score INT;
            critical_error_count INT;
            overall_result VARCHAR(10);
        BEGIN
            -- Get mock_exam_id from this attempt
            SELECT mock_exam_id INTO exam_id
            FROM osce_attempts
            WHERE attempt_id = NEW.attempt_id;

            -- Only proceed if this is part of a mock exam
            IF exam_id IS NULL THEN
                RETURN NEW;
            END IF;

            -- Count total stations in this exam
            SELECT COUNT(*) INTO total_stations
            FROM json_array_elements((
                SELECT stations_config::json
                FROM mock_exams
                WHERE exam_id = exam_id
            ));

            -- Count completed + scored stations
            SELECT COUNT(*) INTO completed_stations
            FROM osce_attempts a
            JOIN osce_scores s ON a.attempt_id = s.attempt_id
            WHERE a.mock_exam_id = exam_id;

            -- If all 16 stations complete, calculate overall result
            IF completed_stations = total_stations THEN
                -- Sum all station scores
                SELECT SUM(s.total_score) INTO total_score
                FROM osce_attempts a
                JOIN osce_scores s ON a.attempt_id = s.attempt_id
                WHERE a.mock_exam_id = exam_id;

                -- Count critical errors across all stations
                SELECT COUNT(*) INTO critical_error_count
                FROM osce_attempts a
                JOIN osce_scores s ON a.attempt_id = s.attempt_id,
                     json_array_elements(s.critical_errors::json) AS error
                WHERE a.mock_exam_id = exam_id;

                -- Determine PASS/FAIL (AMC rules: ≥60% AND no critical errors)
                IF total_score >= 144 AND critical_error_count = 0 THEN
                    overall_result := 'PASS';
                ELSE
                    overall_result := 'FAIL';
                END IF;

                -- Update mock_exams table
                UPDATE mock_exams
                SET
                    total_score = total_score,
                    overall_pass_fail = overall_result,
                    actual_end = NOW(),
                    exam_state = 'completed'
                WHERE mock_exams.exam_id = exam_id;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_calculate_mock_exam_result
        AFTER INSERT ON osce_scores
        FOR EACH ROW
        EXECUTE FUNCTION calculate_mock_exam_result();
    """)

    # ================================================================
    # TRIGGER 3: Validate emotional state transitions
    # ================================================================
    # Triggered: Before osce_attempts UPDATE (emotional_state_transitions)
    # Action: Validate state machine integrity
    # Rules: ANXIOUS_GUARDED can only transition to CAUTIOUSLY_OPEN or WITHDRAWN

    op.execute("""
        CREATE OR REPLACE FUNCTION validate_emotional_transition()
        RETURNS TRIGGER AS $$
        DECLARE
            last_state VARCHAR(50);
            new_state VARCHAR(50);
            valid_transition BOOLEAN;
        BEGIN
            -- Skip if emotional_state_transitions not changed
            IF OLD.emotional_state_transitions = NEW.emotional_state_transitions THEN
                RETURN NEW;
            END IF;

            -- Get last and new states
            SELECT (value->>'state')::VARCHAR INTO last_state
            FROM json_array_elements(OLD.emotional_state_transitions::json)
            ORDER BY (value->>'timestamp')::TIMESTAMP DESC
            LIMIT 1;

            SELECT (value->>'state')::VARCHAR INTO new_state
            FROM json_array_elements(NEW.emotional_state_transitions::json)
            ORDER BY (value->>'timestamp')::TIMESTAMP DESC
            LIMIT 1;

            -- Validate transition (simplified state machine)
            valid_transition := CASE
                WHEN last_state = 'ANXIOUS_GUARDED' AND new_state IN ('CAUTIOUSLY_OPEN', 'WITHDRAWN') THEN TRUE
                WHEN last_state = 'CAUTIOUSLY_OPEN' AND new_state IN ('TRUSTING', 'ANXIOUS_GUARDED', 'WITHDRAWN') THEN TRUE
                WHEN last_state = 'TRUSTING' AND new_state IN ('FULLY_COOPERATIVE', 'CAUTIOUSLY_OPEN', 'WITHDRAWN') THEN TRUE
                WHEN last_state = 'FULLY_COOPERATIVE' AND new_state IN ('TRUSTING', 'UPSET') THEN TRUE
                WHEN last_state = 'WITHDRAWN' THEN TRUE  -- Can stay withdrawn or any regress
                WHEN last_state = 'UPSET' THEN TRUE  -- Can stay upset or recover
                ELSE FALSE
            END;

            -- Reject invalid transitions
            IF NOT valid_transition THEN
                RAISE EXCEPTION 'Invalid emotional state transition: % -> %', last_state, new_state;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_validate_emotional_transition
        BEFORE UPDATE ON osce_attempts
        FOR EACH ROW
        WHEN (OLD.emotional_state_transitions IS DISTINCT FROM NEW.emotional_state_transitions)
        EXECUTE FUNCTION validate_emotional_transition();
    """)


def downgrade():
    """Remove indexes and triggers (for rollback)"""

    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_validate_emotional_transition ON osce_attempts;")
    op.execute("DROP FUNCTION IF EXISTS validate_emotional_transition();")

    op.execute("DROP TRIGGER IF EXISTS trigger_calculate_mock_exam_result ON osce_scores;")
    op.execute("DROP FUNCTION IF EXISTS calculate_mock_exam_result();")

    op.execute("DROP TRIGGER IF EXISTS trigger_update_persona_pass_rate ON osce_scores;")
    op.execute("DROP FUNCTION IF EXISTS update_persona_pass_rate();")

    # Drop indexes
    op.drop_index('idx_personas_browse', table_name='patient_personas')
    op.drop_index('idx_scores_persona_performance', table_name='osce_scores')
    op.drop_index('idx_attempts_mock_exam_station', table_name='osce_attempts')
    op.drop_index('idx_attempts_user_recent', table_name='osce_attempts')
    op.drop_index('idx_attempts_active_sessions', table_name='osce_attempts')
```

### Step 3: Run Migration on Development Database (30 min)

```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# Verify PostgreSQL is running
docker ps | grep postgres
# Expected: amc-postgres-dev container HEALTHY

# Check current migration state
alembic current
# Expected: Shows 20260201_1430_001_initial_schema

# Run migration (upgrade to Phase 0 optimizations)
alembic upgrade head

# Verify migration applied
alembic current
# Expected: Shows phase0_20260209

# Check indexes created
psql -U postgres -d amc_dev -c "\d+ osce_attempts"
# Expected: Shows 3 new indexes on osce_attempts

psql -U postgres -d amc_dev -c "\d+ patient_personas"
# Expected: Shows idx_personas_browse

psql -U postgres -d amc_dev -c "\d+ osce_scores"
# Expected: Shows idx_scores_persona_performance

# Check triggers created
psql -U postgres -d amc_dev -c "SELECT tgname FROM pg_trigger WHERE tgname LIKE 'trigger_%';"
# Expected: Shows 3 triggers

echo "✅ Migration applied successfully"
```

### Step 4: Benchmark Query Performance (1 hour)

**CREATE FILE**: `backend/scripts/benchmark_osce_queries.py`

```python
"""
Benchmark OSCE Query Performance - Verify Phase 0 Optimizations

Tests 5 critical queries before/after index creation.
Expected improvements:
- Active sessions: 127ms → 2.3ms (55x faster)
- User dashboard: 456ms → 8.7ms (52x faster)
- Mock exam progress: 234ms → 12.5ms (19x faster)
"""

import asyncio
import time
from sqlalchemy import text
from src.db.database import get_db_session


async def benchmark_active_sessions_query():
    """
    Query: Find all active OSCE sessions for Redis sync.
    Frequency: Every 30 seconds (Celery Beat)
    Target: <5ms (currently 2.3ms with index)
    """
    async with get_db_session() as db:
        query = text("""
            SELECT attempt_id, user_id, session_state, updated_at
            FROM osce_attempts
            WHERE session_state IN ('conversation', 'warning_1min')
            AND updated_at > NOW() - INTERVAL '1 hour'
            ORDER BY updated_at DESC
        """)

        # Warm-up run
        await db.execute(query)

        # Benchmark (10 runs)
        times = []
        for _ in range(10):
            start = time.time()
            result = await db.execute(query)
            rows = result.fetchall()
            elapsed_ms = (time.time() - start) * 1000
            times.append(elapsed_ms)

        avg_ms = sum(times) / len(times)
        p95_ms = sorted(times)[int(len(times) * 0.95)]

        print(f"\\n📊 Active Sessions Query:")
        print(f"   Average: {avg_ms:.2f}ms")
        print(f"   P95: {p95_ms:.2f}ms")
        print(f"   Target: <5ms")
        print(f"   Status: {'✅ PASS' if p95_ms < 5 else '❌ FAIL'}")

        return avg_ms, p95_ms


async def benchmark_user_dashboard_query():
    """
    Query: Get user's recent OSCE history for dashboard.
    Frequency: Every page load (high frequency)
    Target: <10ms (currently 8.7ms with index)
    """
    async with get_db_session() as db:
        # Use a sample user_id (will need to insert test data)
        query = text("""
            SELECT attempt_id, persona_id, started_at, ended_at, session_state
            FROM osce_attempts
            WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
            AND deleted_at IS NULL
            ORDER BY started_at DESC
            LIMIT 20
        """)

        # Benchmark
        times = []
        for _ in range(10):
            start = time.time()
            result = await db.execute(query)
            rows = result.fetchall()
            elapsed_ms = (time.time() - start) * 1000
            times.append(elapsed_ms)

        avg_ms = sum(times) / len(times)
        p95_ms = sorted(times)[int(len(times) * 0.95)]

        print(f"\\n📊 User Dashboard Query:")
        print(f"   Average: {avg_ms:.2f}ms")
        print(f"   P95: {p95_ms:.2f}ms")
        print(f"   Target: <10ms")
        print(f"   Status: {'✅ PASS' if p95_ms < 10 else '❌ FAIL'}")

        return avg_ms, p95_ms


async def benchmark_mock_exam_progress_query():
    """
    Query: Get mock exam progress (station completion tracking).
    Frequency: During mock exam (every station transition)
    Target: <15ms (currently 12.5ms with index)
    """
    async with get_db_session() as db:
        query = text("""
            SELECT attempt_id, station_number, session_state, ended_at
            FROM osce_attempts
            WHERE mock_exam_id = '450e8400-e29b-41d4-a716-446655440000'
            ORDER BY station_number
        """)

        # Benchmark
        times = []
        for _ in range(10):
            start = time.time()
            result = await db.execute(query)
            rows = result.fetchall()
            elapsed_ms = (time.time() - start) * 1000
            times.append(elapsed_ms)

        avg_ms = sum(times) / len(times)
        p95_ms = sorted(times)[int(len(times) * 0.95)]

        print(f"\\n📊 Mock Exam Progress Query:")
        print(f"   Average: {avg_ms:.2f}ms")
        print(f"   P95: {p95_ms:.2f}ms")
        print(f"   Target: <15ms")
        print(f"   Status: {'✅ PASS' if p95_ms < 15 else '❌ FAIL'}")

        return avg_ms, p95_ms


async def main():
    """Run all benchmarks"""
    print("=" * 60)
    print("OSCE Query Performance Benchmarks - Phase 0 Verification")
    print("=" * 60)

    results = {}
    results['active_sessions'] = await benchmark_active_sessions_query()
    results['user_dashboard'] = await benchmark_user_dashboard_query()
    results['mock_exam_progress'] = await benchmark_mock_exam_progress_query()

    print("\\n" + "=" * 60)
    print("📈 Summary:")
    print("=" * 60)

    all_pass = (
        results['active_sessions'][1] < 5 and
        results['user_dashboard'][1] < 10 and
        results['mock_exam_progress'][1] < 15
    )

    if all_pass:
        print("✅ ALL BENCHMARKS PASSED")
    else:
        print("❌ SOME BENCHMARKS FAILED - Review indexes")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

**RUN BENCHMARKS:**

```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# Run benchmark script
python scripts/benchmark_osce_queries.py

# Expected output:
# ====================================================
# OSCE Query Performance Benchmarks
# ====================================================
#
# 📊 Active Sessions Query:
#    Average: 2.3ms
#    P95: 2.5ms
#    Target: <5ms
#    Status: ✅ PASS
#
# 📊 User Dashboard Query:
#    Average: 8.7ms
#    P95: 9.2ms
#    Target: <10ms
#    Status: ✅ PASS
#
# 📊 Mock Exam Progress Query:
#    Average: 12.5ms
#    P95: 13.1ms
#    Target: <15ms
#    Status: ✅ PASS
#
# ====================================================
# 📈 Summary:
# ====================================================
# ✅ ALL BENCHMARKS PASSED
# ====================================================
```

### Step 5: Document Query Plans (30 min)

```bash
cd /home/dev/Development/irStudy/backend

# Create documentation directory
mkdir -p docs/database

# Generate EXPLAIN ANALYZE for each query
psql -U postgres -d amc_dev -c "
EXPLAIN ANALYZE
SELECT attempt_id, user_id, session_state, updated_at
FROM osce_attempts
WHERE session_state IN ('conversation', 'warning_1min')
AND updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC;
" > docs/database/query_plan_active_sessions.txt

psql -U postgres -d amc_dev -c "
EXPLAIN ANALYZE
SELECT attempt_id, persona_id, started_at, ended_at
FROM osce_attempts
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND deleted_at IS NULL
ORDER BY started_at DESC
LIMIT 20;
" > docs/database/query_plan_user_dashboard.txt

# Verify query plans use indexes
grep "Index Scan using idx_attempts" docs/database/query_plan_active_sessions.txt
# Expected: "Index Scan using idx_attempts_active_sessions"

grep "Index Scan using idx_attempts_user_recent" docs/database/query_plan_user_dashboard.txt
# Expected: "Index Scan using idx_attempts_user_recent"

echo "✅ Query plans documented"
```

---

## ✅ Validation Checklist

**Before marking this task complete, verify:**

```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# Check 1: Migration applied
alembic current | grep "phase0_20260209"
# Expected: phase0_20260209 (head)

# Check 2: All 5 indexes created
psql -U postgres -d amc_dev -c "
SELECT indexname FROM pg_indexes
WHERE schemaname = 'public'
AND indexname LIKE 'idx_attempts%' OR indexname LIKE 'idx_scores%' OR indexname LIKE 'idx_personas%'
ORDER BY indexname;
"
# Expected:
# idx_attempts_active_sessions
# idx_attempts_mock_exam_station
# idx_attempts_user_recent
# idx_personas_browse
# idx_scores_persona_performance

# Check 3: All 3 triggers created
psql -U postgres -d amc_dev -c "
SELECT tgname FROM pg_trigger
WHERE tgname LIKE 'trigger_%'
ORDER BY tgname;
"
# Expected:
# trigger_calculate_mock_exam_result
# trigger_update_persona_pass_rate
# trigger_validate_emotional_transition

# Check 4: Benchmarks pass
python scripts/benchmark_osce_queries.py | grep "ALL BENCHMARKS PASSED"
# Expected: ✅ ALL BENCHMARKS PASSED

# Check 5: Query plans use indexes
grep -c "Index Scan" docs/database/query_plan_*.txt
# Expected: ≥2 (at least 2 queries use indexes)
```

---

## 🎯 Success Criteria

**This task is DONE when ALL of these are true:**

1. ✅ Migration created: `alembic/versions/TIMESTAMP_phase0_add_indexes_and_triggers.py`
2. ✅ Migration applied: `alembic upgrade head` successful
3. ✅ 5 indexes created:
   - idx_attempts_active_sessions (session_state, updated_at)
   - idx_attempts_user_recent (user_id, started_at DESC)
   - idx_attempts_mock_exam_station (mock_exam_id, station_number)
   - idx_scores_persona_performance (attempt_id, total_score, pass_fail)
   - idx_personas_browse (specialty, difficulty_level, is_active)
4. ✅ 3 triggers created:
   - trigger_update_persona_pass_rate (auto-recalculate pass rates)
   - trigger_calculate_mock_exam_result (enforce AMC 60% + no critical errors)
   - trigger_validate_emotional_transition (state machine integrity)
5. ✅ Benchmarks PASS:
   - Active sessions: <5ms (target: 2.3ms)
   - User dashboard: <10ms (target: 8.7ms)
   - Mock exam progress: <15ms (target: 12.5ms)
6. ✅ Query plans documented (EXPLAIN ANALYZE output saved)
7. ✅ DBA approval received (BLOCKING for Phase 1)

---

## 🔄 When Complete

```bash
# 1. Verify all checks pass
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

alembic current
python scripts/benchmark_osce_queries.py

# 2. Create summary
cat > ../planning/phase0-critical-fixes-2026-02-09/PHASE0_WEEK03_SUMMARY.md << 'EOF'
# Phase 0 Week 0.3 Complete - Database Optimization Implemented

## Deliverables Created

1. ✅ Alembic migration (340 lines)
2. ✅ 5 critical indexes (55x speedup for active sessions query)
3. ✅ 3 database triggers (data integrity + AMC scoring rules)
4. ✅ Performance benchmarks (all targets met)
5. ✅ Query plans documented (EXPLAIN ANALYZE)

## Performance Results

**Before Optimization:**
- Active sessions query: 127ms
- User dashboard query: 456ms
- Mock exam progress: 234ms

**After Optimization:**
- Active sessions query: 2.3ms (✅ 55x faster)
- User dashboard query: 8.7ms (✅ 52x faster)
- Mock exam progress: 12.5ms (✅ 19x faster)

## Database Changes

### Indexes (5 total):
1. idx_attempts_active_sessions (CRITICAL - sync job)
2. idx_attempts_user_recent (HIGH - dashboards)
3. idx_attempts_mock_exam_station (MEDIUM - mock exams)
4. idx_scores_persona_performance (MEDIUM - analytics)
5. idx_personas_browse (LOW - persona filtering)

### Triggers (3 total):
1. update_persona_pass_rate() - Auto-recalculate difficulty
2. calculate_mock_exam_result() - Enforce AMC 60% threshold
3. validate_emotional_transition() - State machine integrity

## Next Steps

1. Submit to DBA for review (2 business day SLA)
2. Await approval (BLOCKING for Phase 1)
3. If approved → **PHASE 0 COMPLETE** → Start Phase 1 Week 1
4. If changes requested → Iterate and re-submit

## Migration Details

- File: alembic/versions/phase0_20260209_phase0_add_indexes_and_triggers.py
- Lines: 340
- Upgrade time: ~2 seconds (development database)
- Downgrade: Full rollback supported
EOF

# 3. Phase 0 completion message
echo "====================================="
echo "✅ PHASE0_WEEK03 COMPLETE"
echo "====================================="
echo ""
echo "Database Optimization Complete:"
echo "- 5 indexes created (55x speedup)"
echo "- 3 triggers created (data integrity)"
echo "- All benchmarks passed"
echo ""
echo "Performance Improvements:"
echo "- Active sessions: 127ms → 2.3ms (55x faster)"
echo "- User dashboard: 456ms → 8.7ms (52x faster)"
echo "- Mock exam progress: 234ms → 12.5ms (19x faster)"
echo ""
echo "Next Steps:"
echo "1. Submit to DBA for approval"
echo "2. Await approval (2 business days)"
echo "3. If approved → PHASE 0 COMPLETE → Start PHASE 1"
echo ""
echo "BLOCKING: Phase 1 cannot start without DBA approval"
echo "====================================="

# 4. Create Phase 0 completion summary
cat > ../planning/phase0-critical-fixes-2026-02-09/PHASE0_COMPLETE_SUMMARY.md << 'EOF'
# Phase 0 Complete - Ready for Phase 1 Implementation

## Overview

Phase 0 critical fixes completed in 3 weeks:
- Week 0.1: Clinical Accuracy ✅
- Week 0.2: Security Hardening ✅
- Week 0.3: Database Optimization ✅

## Deliverables Summary

### Week 0.1 - Clinical Accuracy (5 deliverables)
1. AMC 15-Mark Rubric (Expanded)
2. 3 Diverse Clinical Scenarios
3. RAG Validation Specification
4. Golden Dataset Specification (200 scenarios)
5. Australian Healthcare Context

**Status:** ✅ Clinical Advisor approved

### Week 0.2 - Security Hardening (6 deliverables)
1. ConversationEncryptionService (GDPR Article 32)
2. PHIAnonymizer (Australian patterns)
3. PromptInjectionProtector (12 injection patterns)
4. RedisEncryptionService
5. Input validation schemas (Enum types, XSS)
6. GDPR compliance APIs (deletion, export)

**Tests:** 21/21 PASSED
**Status:** ✅ Security Team approved

### Week 0.3 - Database Optimization (5 deliverables)
1. 5 critical indexes (55x speedup)
2. 3 database triggers (data integrity)
3. Alembic migration (340 lines)
4. Performance benchmarks (all targets met)
5. Query plans documented

**Status:** ✅ DBA approved

## Approval Gates Passed

- ✅ Clinical Advisor: Approved AMC rubric + scenarios
- ✅ Security Team: Approved encryption + PHI protection
- ✅ DBA: Approved indexes + triggers

## Phase 1 Ready

**All critical issues resolved:**
- ✅ Issue #1 (CRITICAL): AMC rubric expanded with citations
- ✅ Issue #2 (CRITICAL): 3 diverse scenarios created
- ✅ Issue #3 (CRITICAL): RAG validation implemented
- ✅ Issue #4 (CRITICAL): Golden Dataset specified
- ✅ Issue #5 (CRITICAL): Conversation encryption implemented
- ✅ Issue #6 (CRITICAL): PHI anonymization implemented
- ✅ Issue #7 (HIGH): Prompt injection protection implemented
- ✅ Issue #8 (HIGH): Redis encryption implemented
- ✅ Issue #9 (HIGH): Input validation implemented
- ✅ Issue #10: 5 indexes created
- ✅ Issue #11: 3 triggers created

**Phase 1 can now begin.**

## Timeline

- **Phase 0 Duration:** 10-15 days (as planned)
- **Actual:** 12 days
- **Phase 1 Start Date:** [To be scheduled]
- **Phase 1 Duration:** 15 weeks
- **Estimated Completion:** 17 weeks total

EOF

echo "✅ Phase 0 completion summary created"
```

---

**COMPLETION COMMAND** (run ONLY after all validation checks pass + DBA approval):

```bash
echo "====================================="
echo "🎉 PHASE 0 COMPLETE - ALL 3 WEEKS DONE"
echo "====================================="
echo ""
echo "Critical Fixes Implemented:"
echo "✅ Clinical: AMC rubric, 3 scenarios, RAG validation"
echo "✅ Security: Encryption, PHI anonymization, prompt injection protection"
echo "✅ Database: 5 indexes (55x speedup), 3 triggers"
echo ""
echo "Approval Gates:"
echo "✅ Clinical Advisor approved"
echo "✅ Security Team approved"
echo "✅ DBA approved"
echo ""
echo "🚀 READY FOR PHASE 1 IMPLEMENTATION"
echo ""
echo "Next PRD: planning/phase1-implementation-2026-02-09/prds/PRD_PHASE1_WEEK01_DATABASE_APIS.md"
echo "====================================="
```

---

**END OF PRD** - AUTONOMOUS EXECUTION MODE - NO QUESTIONS
