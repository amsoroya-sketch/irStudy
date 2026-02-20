-- =====================================================
-- TRIGGER VALIDATION TEST SUITE
-- =====================================================
-- Purpose: Comprehensive testing of all 3 database triggers
-- Created: 2026-02-15
-- Run after migration to verify functionality
-- =====================================================

\echo '=================================================='
\echo 'TRIGGER VALIDATION TEST SUITE'
\echo 'Phase 0.3 Day 7 - Database Triggers'
\echo '=================================================='
\echo ''

-- =====================================================
-- TEST 1: updated_at Auto-Update Trigger
-- =====================================================

\echo '=================================================='
\echo 'TEST 1: updated_at Auto-Update Trigger'
\echo '=================================================='
\echo ''

\echo 'Test 1.1: Verify timestamp updates on data change'
\echo '---------------------------------------------------'

-- Get current state
SELECT id, full_name, updated_at
FROM users
WHERE id = 1
LIMIT 1;

\echo ''
\echo 'Updating user record...'

-- Update with actual data change
UPDATE users
SET full_name = 'Trigger Test User - ' || NOW()::TEXT
WHERE id = 1;

\echo ''
\echo 'After update (timestamp should be newer):'

SELECT id, full_name, updated_at
FROM users
WHERE id = 1
LIMIT 1;

\echo ''
\echo 'Test 1.2: Verify NO timestamp update on no-op change'
\echo '------------------------------------------------------'

-- Get current timestamp
SELECT id, email, updated_at
FROM users
WHERE id = 1
LIMIT 1;

-- Store current timestamp for comparison
DO $$
DECLARE
    old_timestamp TIMESTAMP;
    new_timestamp TIMESTAMP;
BEGIN
    SELECT updated_at INTO old_timestamp FROM users WHERE id = 1;

    -- No-op update (set email to same value)
    UPDATE users SET email = (SELECT email FROM users WHERE id = 1) WHERE id = 1;

    SELECT updated_at INTO new_timestamp FROM users WHERE id = 1;

    IF old_timestamp = new_timestamp THEN
        RAISE NOTICE 'PASS: Timestamp unchanged (no-op update)';
    ELSE
        RAISE WARNING 'FAIL: Timestamp changed on no-op update (old: %, new: %)', old_timestamp, new_timestamp;
    END IF;
END $$;

\echo ''

-- =====================================================
-- TEST 2: AMC Score Calculation Trigger
-- =====================================================

\echo '=================================================='
\echo 'TEST 2: AMC Score Calculation Trigger'
\echo '=================================================='
\echo ''

\echo 'Test 2.1: Excellent performance (15/15, pass)'
\echo '----------------------------------------------'

INSERT INTO osce_attempts (user_id, osce_id, scores, time_taken_seconds, attempt_number)
VALUES (
    (SELECT id FROM users LIMIT 1),
    (SELECT id FROM osces LIMIT 1),
    '{
        "communication": 3,
        "clinical_reasoning": 4,
        "information_gathering": 3,
        "management": 3,
        "professionalism": 2,
        "patient_safety_violation": false,
        "professional_misconduct": false,
        "critical_error": false
    }'::json,
    480,
    1
) RETURNING id, total_score, passed, scores->>'communication' AS communication, scores->>'clinical_reasoning' AS clinical_reasoning;

\echo ''
\echo 'Expected: total_score = 15, passed = TRUE'
\echo ''

\echo 'Test 2.2: Borderline performance (9/15, pass)'
\echo '----------------------------------------------'

INSERT INTO osce_attempts (user_id, osce_id, scores, time_taken_seconds, attempt_number)
VALUES (
    (SELECT id FROM users LIMIT 1),
    (SELECT id FROM osces LIMIT 1),
    '{
        "communication": 2,
        "clinical_reasoning": 2,
        "information_gathering": 2,
        "management": 2,
        "professionalism": 1,
        "patient_safety_violation": false,
        "professional_misconduct": false,
        "critical_error": false
    }'::json,
    600,
    1
) RETURNING id, total_score, passed;

\echo ''
\echo 'Expected: total_score = 9, passed = TRUE'
\echo ''

\echo 'Test 2.3: Below threshold (8/15, fail)'
\echo '---------------------------------------'

INSERT INTO osce_attempts (user_id, osce_id, scores, time_taken_seconds, attempt_number)
VALUES (
    (SELECT id FROM users LIMIT 1),
    (SELECT id FROM osces LIMIT 1),
    '{
        "communication": 2,
        "clinical_reasoning": 2,
        "information_gathering": 2,
        "management": 1,
        "professionalism": 1,
        "patient_safety_violation": false,
        "professional_misconduct": false,
        "critical_error": false
    }'::json,
    720,
    1
) RETURNING id, total_score, passed;

\echo ''
\echo 'Expected: total_score = 8, passed = FALSE'
\echo ''

\echo 'Test 2.4: Critical error auto-fail (15/15 but patient safety violation)'
\echo '-----------------------------------------------------------------------'

INSERT INTO osce_attempts (user_id, osce_id, scores, time_taken_seconds, attempt_number)
VALUES (
    (SELECT id FROM users LIMIT 1),
    (SELECT id FROM osces LIMIT 1),
    '{
        "communication": 3,
        "clinical_reasoning": 4,
        "information_gathering": 3,
        "management": 3,
        "professionalism": 2,
        "patient_safety_violation": true,
        "professional_misconduct": false,
        "critical_error": false
    }'::json,
    480,
    1
) RETURNING id, total_score, passed, scores->>'patient_safety_violation' AS patient_safety_violation;

\echo ''
\echo 'Expected: total_score = 15, passed = FALSE (auto-fail on critical error)'
\echo ''

\echo 'Test 2.5: Missing domain score (12/15 but missing minimum)'
\echo '-----------------------------------------------------------'

INSERT INTO osce_attempts (user_id, osce_id, scores, time_taken_seconds, attempt_number)
VALUES (
    (SELECT id FROM users LIMIT 1),
    (SELECT id FROM osces LIMIT 1),
    '{
        "communication": 3,
        "clinical_reasoning": 1,
        "information_gathering": 3,
        "management": 3,
        "professionalism": 2,
        "patient_safety_violation": false,
        "professional_misconduct": false,
        "critical_error": false
    }'::json,
    480,
    1
) RETURNING id, total_score, passed, scores->>'clinical_reasoning' AS clinical_reasoning;

\echo ''
\echo 'Expected: total_score = 12, passed = FALSE (clinical_reasoning = 1 < 2 minimum)'
\echo ''

\echo 'Test 2.6: Invalid score range (should raise error)'
\echo '---------------------------------------------------'

\echo 'Attempting insert with communication score = 5 (max 3)...'

-- This should fail with error
DO $$
BEGIN
    INSERT INTO osce_attempts (user_id, osce_id, scores, time_taken_seconds, attempt_number)
    VALUES (
        (SELECT id FROM users LIMIT 1),
        (SELECT id FROM osces LIMIT 1),
        '{
            "communication": 5,
            "clinical_reasoning": 2,
            "information_gathering": 2,
            "management": 2,
            "professionalism": 1
        }'::json,
        480,
        1
    );
    RAISE WARNING 'FAIL: Invalid score accepted (should have raised exception)';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'PASS: Invalid score rejected with error: %', SQLERRM;
END $$;

\echo ''

-- =====================================================
-- TEST 3: Orphan Response Prevention Trigger
-- =====================================================

\echo '=================================================='
\echo 'TEST 3: Orphan Response Prevention Trigger'
\echo '=================================================='
\echo ''

\echo 'Test 3.1: Prevent deletion of OSCE with attempts'
\echo '-------------------------------------------------'

-- Create test OSCE
INSERT INTO osces (osce_id, station_title, station_type, patient_instructions, candidate_instructions, rubric, specialty, difficulty)
VALUES (
    'TEST-DELETE-001',
    'Test OSCE for Deletion Prevention',
    'history_taking',
    'Test patient instructions',
    'Test candidate instructions',
    '{}'::json,
    'cardiology',
    'easy'
) RETURNING id, station_title;

-- Create student attempt for this OSCE
INSERT INTO osce_attempts (user_id, osce_id, scores, time_taken_seconds, attempt_number)
VALUES (
    (SELECT id FROM users LIMIT 1),
    (SELECT id FROM osces WHERE osce_id = 'TEST-DELETE-001'),
    '{"communication": 2, "clinical_reasoning": 2, "information_gathering": 2, "management": 2, "professionalism": 1}'::json,
    480,
    1
);

\echo ''
\echo 'Attempting to delete OSCE with attempts...'

-- Attempt deletion (should be blocked)
DO $$
DECLARE
    test_osce_id INT;
BEGIN
    SELECT id INTO test_osce_id FROM osces WHERE osce_id = 'TEST-DELETE-001';

    DELETE FROM osces WHERE id = test_osce_id;

    RAISE WARNING 'FAIL: Deletion allowed (should have been blocked)';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'PASS: Deletion blocked with error: %', SQLERRM;
END $$;

\echo ''
\echo 'Test 3.2: Allow deletion of OSCE without attempts'
\echo '---------------------------------------------------'

-- Create test OSCE without attempts
INSERT INTO osces (osce_id, station_title, station_type, patient_instructions, candidate_instructions, rubric, specialty, difficulty)
VALUES (
    'TEST-DELETE-002',
    'Test OSCE for Deletion Allow',
    'history_taking',
    'Test patient instructions',
    'Test candidate instructions',
    '{}'::json,
    'cardiology',
    'easy'
) RETURNING id, station_title;

\echo ''
\echo 'Attempting to delete OSCE without attempts...'

DO $$
DECLARE
    test_osce_id INT;
BEGIN
    SELECT id INTO test_osce_id FROM osces WHERE osce_id = 'TEST-DELETE-002';

    DELETE FROM osces WHERE id = test_osce_id;

    RAISE NOTICE 'PASS: Deletion allowed (no attempts exist)';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'FAIL: Deletion blocked: %', SQLERRM;
END $$;

\echo ''
\echo 'Test 3.3: Soft-delete pattern (recommended approach)'
\echo '-----------------------------------------------------'

-- Soft-delete the OSCE with attempts
UPDATE osces
SET deleted_at = NOW()
WHERE osce_id = 'TEST-DELETE-001'
RETURNING id, station_title, deleted_at;

\echo ''
\echo 'Expected: deleted_at timestamp set, OSCE still in database'
\echo ''

-- Verify OSCE still exists but marked deleted
SELECT id, station_title, deleted_at IS NOT NULL AS is_deleted
FROM osces
WHERE osce_id = 'TEST-DELETE-001';

-- Verify attempts still accessible
SELECT COUNT(*) AS attempt_count
FROM osce_attempts
WHERE osce_id = (SELECT id FROM osces WHERE osce_id = 'TEST-DELETE-001');

\echo ''

-- =====================================================
-- SUMMARY: Verify All Triggers Exist
-- =====================================================

\echo '=================================================='
\echo 'SUMMARY: Verify All Triggers Exist'
\echo '=================================================='
\echo ''

SELECT
    trigger_schema,
    trigger_name,
    event_object_table AS table_name,
    action_timing,
    event_manipulation AS event_type
FROM information_schema.triggers
WHERE trigger_schema = 'public'
  AND trigger_name LIKE 'trigger_%'
ORDER BY event_object_table, trigger_name;

\echo ''
\echo 'Expected: 13 triggers (11 updated_at + 1 score calculation + 1 orphan prevention)'
\echo ''

-- Count triggers
SELECT COUNT(*) AS total_triggers
FROM information_schema.triggers
WHERE trigger_schema = 'public'
  AND trigger_name LIKE 'trigger_%';

\echo ''

-- =====================================================
-- CLEANUP (Optional)
-- =====================================================

\echo '=================================================='
\echo 'CLEANUP: Remove Test Data (Optional)'
\echo '=================================================='
\echo ''

\echo 'Cleaning up test OSCE attempts...'

DELETE FROM osce_attempts
WHERE osce_id IN (
    SELECT id FROM osces WHERE osce_id LIKE 'TEST-DELETE-%'
);

\echo ''
\echo 'Cleaning up test OSCEs...'

DELETE FROM osces WHERE osce_id LIKE 'TEST-DELETE-%';

\echo ''
\echo '=================================================='
\echo 'TRIGGER VALIDATION COMPLETE'
\echo '=================================================='
\echo ''
\echo 'Review output above for PASS/FAIL results.'
\echo 'All tests should show expected behavior.'
\echo ''
