-- ============================================================================
-- Database Performance Optimization - Critical Indexes
-- Created: 2026-02-15 14:53
-- Purpose: Improve query performance across EMR sessions, MCQs, study cards,
--          user progress, and OSCE resources
-- Expected Impact: 10-55x query speedup across 5 critical queries
-- ============================================================================

-- Safety: Use CONCURRENTLY to avoid table locks (production-safe)
-- Note: CONCURRENTLY requires autocommit mode (cannot run inside transaction block)
-- Each CREATE INDEX CONCURRENTLY must be run separately

-- ============================================================================
-- INDEX 1: Active EMR Sessions Lookup (55x speedup target)
-- ============================================================================
-- Partial index: Only indexes rows where status = 'in_progress'
-- Benefits: Fast lookup of active user sessions for dashboard
-- Query: SELECT * FROM emr_sessions
--        WHERE user_id = ? AND status = 'in_progress'
--        ORDER BY started_at DESC

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_emr_sessions_active
ON emr_sessions(user_id, started_at DESC)
WHERE status = 'in_progress' AND deleted_at IS NULL;

-- ============================================================================
-- INDEX 2: MCQ Difficulty + Specialty Filtering (20x speedup target)
-- ============================================================================
-- Composite index: Covers filtering by difficulty, specialty, and sorting by date
-- Benefits: Fast MCQ retrieval for study sessions
-- Query: SELECT * FROM mcqs
--        WHERE difficulty = ? AND specialty = ?
--        ORDER BY created_at DESC LIMIT 20

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcqs_difficulty_specialty
ON mcqs(difficulty, specialty, created_at DESC)
WHERE is_published = TRUE AND deleted_at IS NULL;

-- ============================================================================
-- INDEX 3: Study Cards Due Date Lookup (30x speedup target)
-- ============================================================================
-- Partial index: Only indexes active cards due for review (next 7 days)
-- Benefits: Fast retrieval of cards needing review
-- Query: SELECT * FROM study_cards
--        WHERE user_id = ? AND next_review_date <= CURRENT_DATE
--        AND is_active = TRUE
--        ORDER BY next_review_date ASC
-- Note: This ENHANCES the existing idx_study_cards_user_next_review
--       by adding WHERE clause for even better performance on due cards

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_study_cards_due_optimized
ON study_cards(user_id, next_review_date ASC)
WHERE is_active = TRUE AND deleted_at IS NULL;

-- Note: Original design included "next_review_date <= CURRENT_DATE + INTERVAL '7 days'"
-- in WHERE clause, but PostgreSQL doesn't allow non-immutable functions in partial
-- index predicates. Adjusted to use is_active filter only, which still provides
-- significant performance improvement.

-- ============================================================================
-- INDEX 4: User Progress Specialty Aggregation (15x speedup target)
-- ============================================================================
-- Composite index: Covers user progress queries sorted by update time
-- Benefits: Fast progress dashboard rendering
-- Query: SELECT * FROM user_progress
--        WHERE user_id = ?
--        ORDER BY updated_at DESC

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_progress_specialty_updated
ON user_progress(user_id, specialty, updated_at DESC);

-- ============================================================================
-- INDEX 5: OSCE Specialty + Difficulty Filtering (10x speedup target)
-- ============================================================================
-- Composite index: Covers OSCE browsing ordered by creation date
-- Benefits: Fast OSCE resource filtering and browsing
-- Query: SELECT * FROM osces
--        WHERE specialty = ? AND difficulty = ?
--        ORDER BY created_at DESC LIMIT 20

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_osces_specialty_difficulty
ON osces(specialty, difficulty, created_at DESC)
WHERE is_published = TRUE AND deleted_at IS NULL;

-- ============================================================================
-- Verification Queries (run after index creation)
-- ============================================================================

-- Check indexes created
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('emr_sessions', 'mcqs', 'study_cards', 'user_progress', 'osces')
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Check index sizes
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid::regclass)) as index_size
FROM pg_stat_user_indexes
WHERE indexrelname IN (
    'idx_emr_sessions_active',
    'idx_mcqs_difficulty_specialty',
    'idx_study_cards_due_optimized',
    'idx_user_progress_specialty_updated',
    'idx_osces_specialty_difficulty'
)
ORDER BY pg_relation_size(indexrelid::regclass) DESC;

-- ============================================================================
-- Performance Testing Queries (run BEFORE and AFTER index creation)
-- ============================================================================

-- Test Query 1: Active EMR sessions (expect <5ms after indexing)
EXPLAIN ANALYZE
SELECT * FROM emr_sessions
WHERE user_id = 1 AND status = 'in_progress'
ORDER BY started_at DESC;

-- Test Query 2: MCQ filtering (expect <10ms after indexing)
EXPLAIN ANALYZE
SELECT * FROM mcqs
WHERE difficulty = 'medium' AND specialty = 'cardiology'
ORDER BY created_at DESC
LIMIT 20;

-- Test Query 3: Study cards due (expect <8ms after indexing)
EXPLAIN ANALYZE
SELECT * FROM study_cards
WHERE user_id = 1 AND next_review_date <= CURRENT_DATE
  AND is_active = TRUE
ORDER BY next_review_date ASC;

-- Test Query 4: User progress (expect <12ms after indexing)
EXPLAIN ANALYZE
SELECT * FROM user_progress
WHERE user_id = 1
ORDER BY updated_at DESC;

-- Test Query 5: OSCE filtering (expect <15ms after indexing)
EXPLAIN ANALYZE
SELECT * FROM osces
WHERE specialty = 'cardiology' AND difficulty = 'medium'
ORDER BY created_at DESC
LIMIT 20;

-- ============================================================================
-- Rollback (if needed - use CONCURRENTLY for production safety)
-- ============================================================================

-- DROP INDEX CONCURRENTLY IF EXISTS idx_osces_specialty_difficulty;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_user_progress_specialty_updated;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_study_cards_due_optimized;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_mcqs_difficulty_specialty;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_emr_sessions_active;

-- ============================================================================
-- Notes for DBA
-- ============================================================================

-- 1. Index Creation Time:
--    - Each index takes ~30-60 seconds depending on table size
--    - Total estimated time: 3-5 minutes
--    - No table locks due to CONCURRENTLY

-- 2. Index Maintenance:
--    - Partial indexes are smaller and faster to maintain
--    - Run VACUUM ANALYZE after index creation
--    - Monitor index bloat weekly with pg_stat_user_indexes

-- 3. Production Deployment:
--    - Can be run during business hours (no downtime)
--    - Monitor pg_stat_activity during creation
--    - Verify index usage with pg_stat_user_indexes after 24 hours

-- 4. Monitoring Queries:
SELECT schemaname, tablename, indexname,
       idx_scan as index_scans,
       idx_tup_read as tuples_read,
       idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE indexrelname LIKE 'idx_%'
ORDER BY idx_scan DESC;
