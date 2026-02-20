"""Add EMR practice system tables

Revision ID: 20260215_1200_008
Revises: 20260214_1000_007
Create Date: 2026-02-15 12:00:00

Adds:
- 6 new tables for Epic EHR simulation
- 17 new columns to user_progress for EMR tracking
- All performance indexes for query optimization
- Australian medical compliance fields

Tables:
1. mock_patients - Simulated patient database (500+ cases)
2. emr_sessions - EMR practice session tracking
3. emr_soap_notes - SOAP note documentation
4. emr_prescriptions - PBS-compliant medication orders
5. emr_pathology_orders - MBS pathology requests
6. emr_validation_results - 3-layer validation feedback
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '20260215_1200_008'
down_revision = '20260214_1000_007'
branch_labels = None
depends_on = None


def upgrade():
    """Create EMR tables and extend user_progress."""

    # ================================================================
    # TABLE 1: mock_patients
    # ================================================================
    op.create_table(
        'mock_patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('mrn', sa.String(20), unique=True, nullable=False),
        sa.Column('medicare_number', sa.String(11), nullable=True),

        # Demographics
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('gender', sa.String(20), nullable=False),
        sa.Column('aboriginal_tsi_status', sa.String(50), nullable=True),
        sa.Column('demographics', postgresql.JSON, nullable=False),

        # Clinical Information
        sa.Column('presenting_complaint', sa.Text, nullable=False),
        sa.Column('medical_history', postgresql.JSON, nullable=True),
        sa.Column('medications', postgresql.JSON, nullable=True),
        sa.Column('allergies', postgresql.JSON, nullable=True),
        sa.Column('vital_signs', postgresql.JSON, nullable=True),
        sa.Column('physical_exam_findings', postgresql.JSON, nullable=True),
        sa.Column('investigation_results', postgresql.JSON, nullable=True),

        # Source and Classification
        sa.Column('source_osce_id', sa.Integer, sa.ForeignKey('osces.id'), nullable=True),
        sa.Column('specialty', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('validation_criteria', postgresql.JSON, nullable=True),

        # Metadata
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),

        # Constraints
        sa.CheckConstraint('age >= 18 AND age <= 100', name='check_mock_patients_age_range')
    )

    # Indexes for mock_patients
    op.create_index('idx_mock_patients_specialty', 'mock_patients', ['specialty'])
    op.create_index('idx_mock_patients_difficulty', 'mock_patients', ['difficulty'])
    op.create_index('idx_mock_patients_source_osce', 'mock_patients', ['source_osce_id'])
    op.create_index('idx_mock_patients_mrn', 'mock_patients', ['mrn'])

    # ================================================================
    # TABLE 2: emr_sessions
    # ================================================================
    op.create_table(
        'emr_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('mock_patients.id', ondelete='CASCADE'), nullable=False),

        # Session Metadata
        sa.Column('specialty', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('submitted_at', sa.TIMESTAMP, nullable=True),
        sa.Column('elapsed_time_seconds', sa.Integer, nullable=True),

        # Scoring (AMC 15-mark rubric)
        sa.Column('validation_score', sa.Float, nullable=True),
        sa.Column('score_breakdown', postgresql.JSON, nullable=True),

        # Session Status
        sa.Column('status', sa.String(20), nullable=False, server_default='in_progress'),

        # Performance Metrics
        sa.Column('typing_metrics', postgresql.JSON, nullable=True),
        sa.Column('auto_save_count', sa.Integer, server_default='0'),
        sa.Column('last_auto_save_at', sa.TIMESTAMP, nullable=True),

        # Metadata
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),

        # Constraints
        sa.CheckConstraint('validation_score >= 0 AND validation_score <= 15', name='check_emr_sessions_validation_score')
    )

    # Indexes for emr_sessions
    op.create_index('idx_emr_sessions_user_id', 'emr_sessions', ['user_id'])
    op.create_index('idx_emr_sessions_patient_id', 'emr_sessions', ['patient_id'])
    op.create_index('idx_emr_sessions_started_at', 'emr_sessions', [sa.text('started_at DESC')])
    op.create_index('idx_emr_sessions_specialty', 'emr_sessions', ['specialty'])
    op.create_index('idx_emr_sessions_status', 'emr_sessions', ['status'])
    op.create_index('idx_emr_sessions_user_specialty', 'emr_sessions', ['user_id', 'specialty'])

    # ================================================================
    # TABLE 3: emr_soap_notes
    # ================================================================
    op.create_table(
        'emr_soap_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),

        # SOAP Note Content
        sa.Column('subjective', sa.Text, nullable=True),
        sa.Column('objective', sa.Text, nullable=True),
        sa.Column('assessment', sa.Text, nullable=True),
        sa.Column('plan', sa.Text, nullable=True),
        sa.Column('soap_note_data', postgresql.JSON, nullable=True),

        # Metrics
        sa.Column('word_count', sa.Integer, nullable=True),
        sa.Column('character_count', sa.Integer, nullable=True),
        sa.Column('typing_wpm', sa.Float, nullable=True),

        # Auto-save Tracking
        sa.Column('is_final_submission', sa.Boolean, server_default='false'),
        sa.Column('auto_saved_at', sa.TIMESTAMP, nullable=True),
        sa.Column('version', sa.Integer, server_default='1'),

        # Metadata
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
    )

    # Indexes for emr_soap_notes
    op.create_index('idx_emr_soap_notes_session_id', 'emr_soap_notes', ['session_id'])
    op.create_index('idx_emr_soap_notes_final', 'emr_soap_notes', ['is_final_submission'])

    # ================================================================
    # TABLE 4: emr_prescriptions
    # ================================================================
    op.create_table(
        'emr_prescriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),

        # Prescription Details (Australian Format)
        sa.Column('medication_name', sa.String(200), nullable=False),
        sa.Column('dose', sa.String(50), nullable=False),
        sa.Column('frequency', sa.String(50), nullable=False),
        sa.Column('route', sa.String(20), nullable=False),
        sa.Column('repeats', sa.Integer, nullable=False),
        sa.Column('indication', sa.Text, nullable=True),

        # PBS (Pharmaceutical Benefits Scheme) Validation
        sa.Column('pbs_listed', sa.Boolean, nullable=True),
        sa.Column('pbs_item_code', sa.String(10), nullable=True),
        sa.Column('authority_required', sa.Boolean, nullable=True),

        # Validation Results
        sa.Column('validation_errors', postgresql.JSON, nullable=True),
        sa.Column('is_valid', sa.Boolean, nullable=True),

        # Metadata
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),

        # Constraints
        sa.CheckConstraint('repeats >= 0 AND repeats <= 5', name='check_emr_prescriptions_repeats_range')
    )

    # Indexes for emr_prescriptions
    op.create_index('idx_emr_prescriptions_session_id', 'emr_prescriptions', ['session_id'])
    op.create_index('idx_emr_prescriptions_medication', 'emr_prescriptions', ['medication_name'])

    # ================================================================
    # TABLE 5: emr_pathology_orders
    # ================================================================
    op.create_table(
        'emr_pathology_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),

        # Pathology Test Details
        sa.Column('test_name', sa.String(200), nullable=False),
        sa.Column('test_category', sa.String(50), nullable=True),
        sa.Column('mbs_item_number', sa.String(10), nullable=True),
        sa.Column('urgency', sa.String(20), nullable=False, server_default='routine'),
        sa.Column('indication', sa.Text, nullable=True),

        # Validation
        sa.Column('appropriate', sa.Boolean, nullable=True),
        sa.Column('validation_feedback', postgresql.JSON, nullable=True),

        # Metadata
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
    )

    # Indexes for emr_pathology_orders
    op.create_index('idx_emr_pathology_orders_session_id', 'emr_pathology_orders', ['session_id'])
    op.create_index('idx_emr_pathology_orders_urgency', 'emr_pathology_orders', ['urgency'])
    op.create_index('idx_emr_pathology_orders_test_name', 'emr_pathology_orders', ['test_name'])

    # ================================================================
    # TABLE 6: emr_validation_results
    # ================================================================
    op.create_table(
        'emr_validation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),

        # Validation Type
        sa.Column('validation_type', sa.String(50), nullable=False),

        # 3-Layer Validation Results
        sa.Column('layer_1_zod', postgresql.JSON, nullable=True),
        sa.Column('layer_2_python', postgresql.JSON, nullable=True),
        sa.Column('layer_3_ai', postgresql.JSON, nullable=True),

        # Overall Validation Summary
        sa.Column('overall_score', sa.Float, nullable=True),
        sa.Column('passed', sa.Boolean, nullable=True),

        # Extracted Feedback (for UI display)
        sa.Column('strengths', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('improvements', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('red_flags', postgresql.ARRAY(sa.Text), nullable=True),

        # Metadata
        sa.Column('validated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),

        # Constraints
        sa.CheckConstraint('overall_score >= 0 AND overall_score <= 15', name='check_emr_validation_overall_score')
    )

    # Indexes for emr_validation_results
    op.create_index('idx_emr_validation_results_session_id', 'emr_validation_results', ['session_id'])
    op.create_index('idx_emr_validation_results_type', 'emr_validation_results', ['validation_type'])
    op.create_index('idx_emr_validation_results_validated_at', 'emr_validation_results', [sa.text('validated_at DESC')])

    # ================================================================
    # EXTEND user_progress TABLE (17 new columns)
    # ================================================================

    # EMR General Metrics
    op.add_column('user_progress', sa.Column('emr_sessions_completed', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_soap_notes_written', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_average_score', sa.Float, server_default='0.0'))
    op.add_column('user_progress', sa.Column('emr_total_time_minutes', sa.Integer, server_default='0'))

    # Specialty-specific EMR columns (10 specialties)
    op.add_column('user_progress', sa.Column('emr_cardiology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_respiratory_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_gastroenterology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_neurology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_endocrinology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_rheumatology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_haematology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_renal_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_infectious_diseases_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_emergency_medicine_sessions', sa.Integer, server_default='0'))

    # Performance metrics
    op.add_column('user_progress', sa.Column('emr_pass_rate', sa.Float, server_default='0.0'))
    op.add_column('user_progress', sa.Column('emr_highest_score', sa.Float, server_default='0.0'))
    op.add_column('user_progress', sa.Column('emr_last_session_date', sa.Date, nullable=True))


def downgrade():
    """Remove EMR tables and user_progress extensions."""

    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('emr_validation_results')
    op.drop_table('emr_pathology_orders')
    op.drop_table('emr_prescriptions')
    op.drop_table('emr_soap_notes')
    op.drop_table('emr_sessions')
    op.drop_table('mock_patients')

    # Remove user_progress columns
    op.drop_column('user_progress', 'emr_last_session_date')
    op.drop_column('user_progress', 'emr_highest_score')
    op.drop_column('user_progress', 'emr_pass_rate')

    op.drop_column('user_progress', 'emr_emergency_medicine_sessions')
    op.drop_column('user_progress', 'emr_infectious_diseases_sessions')
    op.drop_column('user_progress', 'emr_renal_sessions')
    op.drop_column('user_progress', 'emr_haematology_sessions')
    op.drop_column('user_progress', 'emr_rheumatology_sessions')
    op.drop_column('user_progress', 'emr_endocrinology_sessions')
    op.drop_column('user_progress', 'emr_neurology_sessions')
    op.drop_column('user_progress', 'emr_gastroenterology_sessions')
    op.drop_column('user_progress', 'emr_respiratory_sessions')
    op.drop_column('user_progress', 'emr_cardiology_sessions')

    op.drop_column('user_progress', 'emr_total_time_minutes')
    op.drop_column('user_progress', 'emr_average_score')
    op.drop_column('user_progress', 'emr_soap_notes_written')
    op.drop_column('user_progress', 'emr_sessions_completed')
