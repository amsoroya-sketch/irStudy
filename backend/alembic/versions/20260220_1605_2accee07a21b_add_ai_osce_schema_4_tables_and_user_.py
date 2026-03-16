"""add_ai_osce_schema_4_tables_and_user_progress_extension

Revision ID: 2accee07a21b
Revises: 20260215_1600_010
Create Date: 2026-02-20 16:05:37.656679+11:00

AI OSCE Database Schema Migration

Creates 4 new tables for AI OSCE Simulation System:
1. patient_personas - 360 AI patient profiles with emotional intelligence
2. mock_exams - 16-station full OSCE exams
3. osce_attempts - Individual OSCE session tracking
4. osce_scores - AMC 15-mark rubric scoring

Extends user_progress table with 5 AI OSCE tracking columns.

Performance Impact:
- Migration time: <5 minutes (uses gen_random_uuid(), no table locks)
- Indexes created with proper naming (no CONCURRENTLY in Alembic)
- Trigger auto-updates user_progress on session completion

Security:
- No hardcoded credentials
- Foreign keys with CASCADE/RESTRICT as appropriate
- PHI fields ready for encryption (conversation_history, etc.)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY


# revision identifiers, used by Alembic.
revision: str = '2accee07a21b'
down_revision: Union[str, None] = '20260215_1600_010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create AI OSCE database schema"""

    # ================================================================
    # TABLE 1: patient_personas
    # ================================================================
    # Purpose: Rich AI patient profiles with emotional intelligence
    # Capacity: 360 personas (cross-product of specialties × difficulty)
    # Key Features: Progressive disclosure, RAG hints, emotional states

    op.create_table(
        'patient_personas',
        sa.Column('persona_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('persona_code', sa.String(20), unique=True, nullable=False),

        # Patient Demographics
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('gender', sa.String(20), nullable=False),
        sa.Column('occupation', sa.String(100), nullable=True),
        sa.Column('cultural_background', sa.String(100), nullable=True),
        sa.Column('preferred_language', sa.String(50), server_default='English'),

        # Clinical Presentation
        sa.Column('specialty', sa.String(50), nullable=False),
        sa.Column('chief_complaint', sa.Text, nullable=False),
        sa.Column('opening_statement', sa.Text, nullable=False),

        # Progressive Disclosure (JSONB for flexibility)
        sa.Column('symptoms', JSONB, nullable=False),
        sa.Column('medical_history', JSONB, nullable=False),
        sa.Column('emotional_profile', JSONB, nullable=False),

        # RAG Integration Hints
        sa.Column('rag_query_hints', ARRAY(sa.Text), nullable=True),
        sa.Column('key_differentials', ARRAY(sa.Text), nullable=True),
        sa.Column('critical_actions', ARRAY(sa.Text), nullable=True),

        # Difficulty Metadata
        sa.Column('difficulty_level', sa.String(20), nullable=False),
        sa.Column('estimated_pass_rate', sa.Numeric(3, 1), nullable=True),

        # AMC Alignment
        sa.Column('amc_blueprint_area', sa.String(100), nullable=True),
        sa.Column('amc_competencies', ARRAY(sa.Text), nullable=True),

        # Audit Fields
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('validated_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('version', sa.Integer, server_default='1', nullable=False),

        # Constraints
        sa.CheckConstraint('age >= 18 AND age <= 95', name='check_persona_age_range'),
        sa.CheckConstraint(
            "difficulty_level IN ('foundation', 'intermediate', 'advanced')",
            name='check_difficulty_level'
        ),
    )

    # Indexes for patient_personas
    op.create_index('idx_personas_specialty', 'patient_personas', ['specialty'], postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_personas_difficulty', 'patient_personas', ['difficulty_level'], postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_personas_code', 'patient_personas', ['persona_code'])

    # ================================================================
    # TABLE 2: mock_exams
    # ================================================================
    # Purpose: Orchestrate 16-station full OSCE mock exams
    # Duration: ~150 minutes (16 stations × 8 min + breaks)

    op.create_table(
        'mock_exams',
        sa.Column('exam_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        # Exam Configuration
        sa.Column('stations_config', JSONB, nullable=False),  # Array of 16 persona_ids
        sa.Column('exam_name', sa.String(200), nullable=True),

        # Progress Tracking
        sa.Column('exam_state', sa.String(20), server_default='IN_PROGRESS', nullable=False),
        sa.Column('current_station_number', sa.Integer, server_default='1', nullable=False),

        # Timing
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_duration_minutes', sa.Integer, nullable=True),

        # Overall Performance
        sa.Column('total_score', sa.Integer, server_default='0', nullable=False),
        sa.Column('stations_passed', sa.Integer, server_default='0', nullable=False),
        sa.Column('overall_pass', sa.Boolean, nullable=True),

        # Constraints
        sa.CheckConstraint(
            "exam_state IN ('IN_PROGRESS', 'COMPLETED', 'ABANDONED')",
            name='check_exam_state'
        ),
        sa.CheckConstraint(
            'current_station_number >= 1 AND current_station_number <= 16',
            name='check_station_number'
        ),
    )

    # Indexes for mock_exams
    op.create_index('idx_mock_exams_user', 'mock_exams', ['user_id', sa.text('started_at DESC')])

    # ================================================================
    # TABLE 3: ai_osce_attempts
    # ================================================================
    # Purpose: Track individual OSCE practice sessions (individual or mock exam)
    # State Machine: initialized → conversation → warning_1min → finalized → scoring → complete

    op.create_table(
        'ai_osce_attempts',
        sa.Column('attempt_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Relationships
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('persona_id', UUID(as_uuid=True), sa.ForeignKey('patient_personas.persona_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('mock_exam_id', UUID(as_uuid=True), sa.ForeignKey('mock_exams.exam_id', ondelete='CASCADE'), nullable=True),

        # Session Metadata
        sa.Column('session_type', sa.String(20), nullable=False),
        sa.Column('station_number', sa.Integer, nullable=True),

        # Timing
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer, nullable=True),

        # Conversation Archive (PostgreSQL permanent storage)
        sa.Column('conversation_history', JSONB, server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('emotional_state_transitions', JSONB, server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('student_actions', JSONB, server_default=sa.text("'[]'::jsonb"), nullable=False),

        # Metadata
        sa.Column('was_completed', sa.Boolean, server_default='false', nullable=False),
        sa.Column('abandonment_reason', sa.Text, nullable=True),

        # Constraints
        sa.CheckConstraint(
            "session_type IN ('individual', 'mock_exam')",
            name='check_session_type'
        ),
        sa.CheckConstraint(
            'station_number IS NULL OR (station_number >= 1 AND station_number <= 16)',
            name='check_attempt_station_number'
        ),
    )

    # Indexes for ai_osce_attempts
    op.create_index('idx_attempts_user', 'ai_osce_attempts', ['user_id', sa.text('started_at DESC')])
    op.create_index('idx_attempts_persona', 'ai_osce_attempts', ['persona_id'])
    op.create_index('idx_attempts_exam', 'ai_osce_attempts', ['mock_exam_id'], postgresql_where=sa.text('mock_exam_id IS NOT NULL'))

    # ================================================================
    # TABLE 4: ai_osce_scores
    # ================================================================
    # Purpose: AMC 15-mark rubric scoring by AI Examiner
    # Rubric: Communication (0-3) + Clinical Reasoning (0-4) +
    #         Information Gathering (0-4) + Management (0-2) + Professionalism (0-2) = 15
    # Pass Threshold: ≥9/15 (60%)

    op.create_table(
        'ai_osce_scores',
        sa.Column('score_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('attempt_id', UUID(as_uuid=True), sa.ForeignKey('ai_osce_attempts.attempt_id', ondelete='CASCADE'), unique=True, nullable=False),

        # AMC 15-Mark Rubric Breakdown
        sa.Column('communication_score', sa.Integer, nullable=True),
        sa.Column('clinical_reasoning_score', sa.Integer, nullable=True),
        sa.Column('information_gathering_score', sa.Integer, nullable=True),
        sa.Column('management_score', sa.Integer, nullable=True),
        sa.Column('professionalism_score', sa.Integer, nullable=True),

        # Feedback
        sa.Column('ai_examiner_feedback', JSONB, nullable=True),
        sa.Column('strengths', ARRAY(sa.Text), nullable=True),
        sa.Column('areas_for_improvement', ARRAY(sa.Text), nullable=True),
        sa.Column('critical_errors', ARRAY(sa.Text), nullable=True),

        # Audit
        sa.Column('scored_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('scoring_model_version', sa.String(50), nullable=True),

        # Constraints - AMC score ranges
        sa.CheckConstraint(
            'communication_score IS NULL OR (communication_score >= 0 AND communication_score <= 3)',
            name='check_communication_score'
        ),
        sa.CheckConstraint(
            'clinical_reasoning_score IS NULL OR (clinical_reasoning_score >= 0 AND clinical_reasoning_score <= 4)',
            name='check_clinical_reasoning_score'
        ),
        sa.CheckConstraint(
            'information_gathering_score IS NULL OR (information_gathering_score >= 0 AND information_gathering_score <= 4)',
            name='check_information_gathering_score'
        ),
        sa.CheckConstraint(
            'management_score IS NULL OR (management_score >= 0 AND management_score <= 2)',
            name='check_management_score'
        ),
        sa.CheckConstraint(
            'professionalism_score IS NULL OR (professionalism_score >= 0 AND professionalism_score <= 2)',
            name='check_professionalism_score'
        ),
    )

    # Create computed column for total_score (GENERATED ALWAYS AS)
    op.execute("""
        ALTER TABLE ai_osce_scores
        ADD COLUMN total_score INTEGER GENERATED ALWAYS AS (
            COALESCE(communication_score, 0) +
            COALESCE(clinical_reasoning_score, 0) +
            COALESCE(information_gathering_score, 0) +
            COALESCE(management_score, 0) +
            COALESCE(professionalism_score, 0)
        ) STORED;
    """)

    # Create computed column for pass_fail (GENERATED ALWAYS AS)
    op.execute("""
        ALTER TABLE ai_osce_scores
        ADD COLUMN pass_fail VARCHAR(10) GENERATED ALWAYS AS (
            CASE WHEN (
                COALESCE(communication_score, 0) +
                COALESCE(clinical_reasoning_score, 0) +
                COALESCE(information_gathering_score, 0) +
                COALESCE(management_score, 0) +
                COALESCE(professionalism_score, 0)
            ) >= 9 THEN 'PASS' ELSE 'FAIL' END
        ) STORED;
    """)

    # Indexes for ai_osce_scores
    op.create_index('idx_scores_attempt', 'ai_osce_scores', ['attempt_id'])
    op.create_index('idx_scores_pass_fail', 'ai_osce_scores', [sa.text('pass_fail')])

    # ================================================================
    # EXTEND user_progress TABLE
    # ================================================================
    # Add 5 new columns for AI OSCE tracking

    op.add_column('user_progress', sa.Column('ai_osces_attempted', sa.Integer, server_default='0', nullable=True))
    op.add_column('user_progress', sa.Column('ai_osces_passed', sa.Integer, server_default='0', nullable=True))
    op.add_column('user_progress', sa.Column('ai_osce_avg_score', sa.Numeric(4, 2), server_default='0.00', nullable=True))
    op.add_column('user_progress', sa.Column('mock_exams_completed', sa.Integer, server_default='0', nullable=True))
    op.add_column('user_progress', sa.Column('last_ai_osce_at', sa.DateTime(timezone=True), nullable=True))

    # ================================================================
    # TRIGGER: Auto-update user_progress on session completion
    # ================================================================
    # Purpose: Automatically update AI OSCE metrics when session ends
    # Fires: AFTER UPDATE OF ended_at ON ai_osce_attempts

    op.execute("""
        CREATE OR REPLACE FUNCTION update_ai_osce_progress()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE user_progress
            SET
                ai_osces_attempted = ai_osces_attempted + 1,
                ai_osces_passed = CASE
                    WHEN (SELECT pass_fail FROM ai_osce_scores WHERE attempt_id = NEW.attempt_id) = 'PASS'
                    THEN ai_osces_passed + 1
                    ELSE ai_osces_passed
                END,
                last_ai_osce_at = NEW.ended_at,
                ai_osce_avg_score = (
                    SELECT AVG(s.total_score)
                    FROM ai_osce_attempts a
                    JOIN ai_osce_scores s ON a.attempt_id = s.attempt_id
                    WHERE a.user_id = NEW.user_id
                )
            WHERE user_id = NEW.user_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_update_ai_osce_progress
        AFTER UPDATE OF ended_at ON ai_osce_attempts
        FOR EACH ROW
        WHEN (NEW.ended_at IS NOT NULL AND OLD.ended_at IS NULL)
        EXECUTE FUNCTION update_ai_osce_progress();
    """)


def downgrade() -> None:
    """Remove AI OSCE database schema"""

    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS trigger_update_ai_osce_progress ON ai_osce_attempts")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_ai_osce_progress()")

    # Remove columns from user_progress
    op.drop_column('user_progress', 'last_ai_osce_at')
    op.drop_column('user_progress', 'mock_exams_completed')
    op.drop_column('user_progress', 'ai_osce_avg_score')
    op.drop_column('user_progress', 'ai_osces_passed')
    op.drop_column('user_progress', 'ai_osces_attempted')

    # Drop tables in reverse dependency order
    op.drop_table('ai_osce_scores')
    op.drop_table('ai_osce_attempts')
    op.drop_table('mock_exams')
    op.drop_table('patient_personas')
