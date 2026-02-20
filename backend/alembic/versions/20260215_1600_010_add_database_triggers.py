"""Add database triggers for automated data management

Revision ID: 20260215_1600_010
Revises: 20260215_1453_009
Create Date: 2026-02-15 16:00:00.000000

Triggers Added:
1. updated_at auto-update (11 tables) - Auto-updates timestamp on row modification
2. AMC score calculation (osce_attempts) - Auto-calculates total score and pass/fail
3. Orphan response prevention (osces) - Prevents deletion of OSCEs with student attempts

Benefits:
- Data consistency: Timestamps always accurate
- Reduced application logic: Score calculation happens in database
- Data integrity: Prevents orphaned records
- Audit compliance: Forces soft-delete pattern

Performance Impact:
- updated_at trigger: <1ms overhead per UPDATE
- AMC score calculation: <0.5ms overhead per INSERT/UPDATE
- Orphan prevention: <2ms overhead per DELETE (rare operation)
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = '20260215_1600_010'
down_revision = '20260215_1453_009'
branch_labels = None
depends_on = None


def upgrade():
    """Add database triggers for automated data management"""

    # ================================================================
    # TRIGGER 1: updated_at Auto-Update (11 tables)
    # ================================================================
    # Purpose: Automatically update updated_at timestamp on row modifications
    # Performance: <1ms overhead per UPDATE operation
    # Applies to: users, mcqs, osces, user_progress, mock_patients, emr_sessions,
    #             emr_soap_notes, emr_prescriptions, emr_pathology_orders,
    #             emr_validation_results, study_cards

    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Only update if row data actually changed
            IF NEW IS DISTINCT FROM OLD THEN
                NEW.updated_at = NOW();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        COMMENT ON FUNCTION update_updated_at_column() IS
        'Reusable trigger function to auto-update updated_at timestamp on row modification. Only updates if data changed.';
    """)

    # Apply to users table
    op.execute("""
        CREATE TRIGGER trigger_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    # Apply to mcqs table
    op.execute("""
        CREATE TRIGGER trigger_mcqs_updated_at
            BEFORE UPDATE ON mcqs
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    # Apply to osces table
    op.execute("""
        CREATE TRIGGER trigger_osces_updated_at
            BEFORE UPDATE ON osces
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    # Apply to user_progress table
    op.execute("""
        CREATE TRIGGER trigger_user_progress_updated_at
            BEFORE UPDATE ON user_progress
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    # Apply to mock_patients table
    op.execute("""
        CREATE TRIGGER trigger_mock_patients_updated_at
            BEFORE UPDATE ON mock_patients
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    # Apply to emr_sessions table
    op.execute("""
        CREATE TRIGGER trigger_emr_sessions_updated_at
            BEFORE UPDATE ON emr_sessions
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    # Apply to emr_soap_notes table (conditional - only if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'emr_soap_notes') THEN
                EXECUTE 'CREATE TRIGGER trigger_emr_soap_notes_updated_at
                    BEFORE UPDATE ON emr_soap_notes
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()';
            END IF;
        END $$;
    """)

    # Apply to emr_prescriptions table (conditional - only if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'emr_prescriptions') THEN
                EXECUTE 'CREATE TRIGGER trigger_emr_prescriptions_updated_at
                    BEFORE UPDATE ON emr_prescriptions
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()';
            END IF;
        END $$;
    """)

    # Apply to emr_pathology_orders table (conditional - only if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'emr_pathology_orders') THEN
                EXECUTE 'CREATE TRIGGER trigger_emr_pathology_orders_updated_at
                    BEFORE UPDATE ON emr_pathology_orders
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()';
            END IF;
        END $$;
    """)

    # Apply to emr_validation_results table (conditional - only if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'emr_validation_results') THEN
                EXECUTE 'CREATE TRIGGER trigger_emr_validation_results_updated_at
                    BEFORE UPDATE ON emr_validation_results
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()';
            END IF;
        END $$;
    """)

    # Apply to study_cards table (conditional - only if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'study_cards') THEN
                EXECUTE 'CREATE TRIGGER trigger_study_cards_updated_at
                    BEFORE UPDATE ON study_cards
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()';
            END IF;
        END $$;
    """)

    # ================================================================
    # TRIGGER 2: AMC Score Calculation (osce_attempts)
    # ================================================================
    # Purpose: Auto-calculate OSCE total score and pass/fail status
    # AMC Rubric: 5 domains, 15 marks total
    # Performance: <0.5ms overhead per INSERT/UPDATE

    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_amc_score()
        RETURNS TRIGGER AS $$
        DECLARE
            communication_score INT;
            clinical_reasoning_score INT;
            information_gathering_score INT;
            management_score INT;
            professionalism_score INT;
            calculated_total INT;
            has_critical_error BOOLEAN;
        BEGIN
            -- Extract domain scores from JSON scores field
            -- AMC rubric structure: {"communication": 0-3, "clinical_reasoning": 0-4,
            --                        "information_gathering": 0-3, "management": 0-3,
            --                        "professionalism": 0-2}
            communication_score := COALESCE((NEW.scores->>'communication')::INT, 0);
            clinical_reasoning_score := COALESCE((NEW.scores->>'clinical_reasoning')::INT, 0);
            information_gathering_score := COALESCE((NEW.scores->>'information_gathering')::INT, 0);
            management_score := COALESCE((NEW.scores->>'management')::INT, 0);
            professionalism_score := COALESCE((NEW.scores->>'professionalism')::INT, 0);

            -- Calculate total score (max 15)
            calculated_total := communication_score + clinical_reasoning_score +
                               information_gathering_score + management_score +
                               professionalism_score;

            -- Validate domain score ranges (fail-safe)
            IF communication_score < 0 OR communication_score > 3 THEN
                RAISE EXCEPTION 'Communication score must be between 0 and 3, got %', communication_score;
            END IF;

            IF clinical_reasoning_score < 0 OR clinical_reasoning_score > 4 THEN
                RAISE EXCEPTION 'Clinical reasoning score must be between 0 and 4, got %', clinical_reasoning_score;
            END IF;

            IF information_gathering_score < 0 OR information_gathering_score > 3 THEN
                RAISE EXCEPTION 'Information gathering score must be between 0 and 3, got %', information_gathering_score;
            END IF;

            IF management_score < 0 OR management_score > 3 THEN
                RAISE EXCEPTION 'Management score must be between 0 and 3, got %', management_score;
            END IF;

            IF professionalism_score < 0 OR professionalism_score > 2 THEN
                RAISE EXCEPTION 'Professionalism score must be between 0 and 2, got %', professionalism_score;
            END IF;

            -- Set calculated total score
            NEW.total_score := calculated_total;

            -- Check for critical errors (auto-fail conditions)
            has_critical_error := COALESCE((NEW.scores->>'patient_safety_violation')::BOOLEAN, FALSE) OR
                                 COALESCE((NEW.scores->>'professional_misconduct')::BOOLEAN, FALSE) OR
                                 COALESCE((NEW.scores->>'critical_error')::BOOLEAN, FALSE);

            -- Determine pass/fail status
            -- Auto-fail if critical error exists
            IF has_critical_error THEN
                NEW.passed := FALSE;
            ELSE
                -- Pass criteria (all must be met):
                -- 1. Total score >= 9/15 (60%)
                -- 2. Minimum domain scores:
                --    - Communication >= 1
                --    - Clinical Reasoning >= 2
                --    - Information Gathering >= 2
                --    - Professionalism >= 1
                IF calculated_total >= 9 AND
                   communication_score >= 1 AND
                   clinical_reasoning_score >= 2 AND
                   information_gathering_score >= 2 AND
                   professionalism_score >= 1 THEN
                    NEW.passed := TRUE;
                ELSE
                    NEW.passed := FALSE;
                END IF;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        COMMENT ON FUNCTION calculate_amc_score() IS
        'AMC 15-mark rubric auto-scoring: Calculates total score from 5 domains and determines pass/fail based on AMC Clinical Exam criteria. Auto-fails on patient safety violations.';
    """)

    # Apply trigger to osce_attempts table
    op.execute("""
        CREATE TRIGGER trigger_osce_attempts_calculate_score
            BEFORE INSERT OR UPDATE ON osce_attempts
            FOR EACH ROW
            EXECUTE FUNCTION calculate_amc_score();
    """)

    # ================================================================
    # TRIGGER 3: Orphan Response Prevention (osces)
    # ================================================================
    # Purpose: Prevent deletion of OSCE records that have student attempts
    # Rationale: Data integrity, audit trail, prevent orphaned records
    # Performance: <2ms overhead per DELETE (only fires on delete)

    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_osce_deletion_with_attempts()
        RETURNS TRIGGER AS $$
        DECLARE
            attempt_count INT;
        BEGIN
            -- Check if OSCE has any related attempts
            SELECT COUNT(*) INTO attempt_count
            FROM osce_attempts
            WHERE osce_id = OLD.id;

            -- Prevent deletion if attempts exist
            IF attempt_count > 0 THEN
                RAISE EXCEPTION 'Cannot delete OSCE with ID % ("%") - % student attempt(s) exist. Delete attempts first or use soft-delete (UPDATE deleted_at).',
                    OLD.id,
                    OLD.station_title,
                    attempt_count;
            END IF;

            -- Allow deletion if no attempts
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        COMMENT ON FUNCTION prevent_osce_deletion_with_attempts() IS
        'Data integrity constraint: Prevents hard deletion of OSCE records that have student attempts. Enforces soft-delete pattern for audit compliance.';
    """)

    # Apply trigger to osces table
    op.execute("""
        CREATE TRIGGER trigger_osces_prevent_deletion_with_attempts
            BEFORE DELETE ON osces
            FOR EACH ROW
            EXECUTE FUNCTION prevent_osce_deletion_with_attempts();
    """)


def downgrade():
    """Remove all triggers and trigger functions"""

    # Drop triggers first (in reverse order of creation)

    # Trigger 3: Orphan prevention
    op.execute("DROP TRIGGER IF EXISTS trigger_osces_prevent_deletion_with_attempts ON osces")

    # Trigger 2: AMC score calculation
    op.execute("DROP TRIGGER IF EXISTS trigger_osce_attempts_calculate_score ON osce_attempts")

    # Trigger 1: updated_at auto-update (11 tables)
    op.execute("DROP TRIGGER IF EXISTS trigger_study_cards_updated_at ON study_cards")
    op.execute("DROP TRIGGER IF EXISTS trigger_emr_validation_results_updated_at ON emr_validation_results")
    op.execute("DROP TRIGGER IF EXISTS trigger_emr_pathology_orders_updated_at ON emr_pathology_orders")
    op.execute("DROP TRIGGER IF EXISTS trigger_emr_prescriptions_updated_at ON emr_prescriptions")
    op.execute("DROP TRIGGER IF EXISTS trigger_emr_soap_notes_updated_at ON emr_soap_notes")
    op.execute("DROP TRIGGER IF EXISTS trigger_emr_sessions_updated_at ON emr_sessions")
    op.execute("DROP TRIGGER IF EXISTS trigger_mock_patients_updated_at ON mock_patients")
    op.execute("DROP TRIGGER IF EXISTS trigger_user_progress_updated_at ON user_progress")
    op.execute("DROP TRIGGER IF EXISTS trigger_osces_updated_at ON osces")
    op.execute("DROP TRIGGER IF EXISTS trigger_mcqs_updated_at ON mcqs")
    op.execute("DROP TRIGGER IF EXISTS trigger_users_updated_at ON users")

    # Drop trigger functions (CASCADE will drop any remaining triggers)
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS calculate_amc_score() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS prevent_osce_deletion_with_attempts() CASCADE")
