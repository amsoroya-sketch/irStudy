"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-02-01 14:30:00

TABLES:
- users: User accounts with HIPAA-compliant security
- mcqs: Multiple-choice questions with Australian medical context
- osces: OSCE scenarios with AMC Clinical Exam rubrics
- mcq_attempts: Individual MCQ attempt records with audit trail
- user_progress: Progress tracking with learning analytics
- user_favorite_mcqs: Many-to-many relationship (users ↔ mcqs)
- user_favorite_osces: Many-to-many relationship (users ↔ osces)

SECURITY:
- Passwords hashed with bcrypt (never plaintext)
- PHI encrypted at application layer
- Soft deletes for audit compliance
- Timestamps on all records
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema"""

    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('student', 'educator', 'admin')")
    op.execute("CREATE TYPE difficultylevel AS ENUM ('easy', 'medium', 'hard')")
    op.execute("""
        CREATE TYPE medicalspecialty AS ENUM (
            'cardiology', 'respiratory', 'gastroenterology', 'neurology',
            'psychiatry', 'endocrinology', 'emergency_medicine', 'general_practice',
            'paediatrics', 'obstetrics_gynaecology', 'surgery'
        )
    """)
    op.execute("""
        CREATE TYPE oscetype AS ENUM (
            'history_taking', 'physical_examination', 'counselling',
            'communication', 'diagnosis_management', 'emergency_scenario'
        )
    """)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', postgresql.ENUM(name='userrole', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Create mcqs table
    op.create_table(
        'mcqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.String(length=50), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('correct_answer', sa.String(length=1), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('citation', sa.String(length=500), nullable=False),
        sa.Column('learning_points', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('specialty', postgresql.ENUM(name='medicalspecialty', create_type=False), nullable=False),
        sa.Column('difficulty', postgresql.ENUM(name='difficultylevel', create_type=False), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('image_caption', sa.String(length=500), nullable=True),
        sa.Column('times_attempted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('times_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_time_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('requires_australian_context', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_id')
    )
    op.create_index('ix_mcqs_id', 'mcqs', ['id'])
    op.create_index('ix_mcqs_question_id', 'mcqs', ['question_id'])
    op.create_index('ix_mcqs_specialty', 'mcqs', ['specialty'])

    # Create osces table
    op.create_table(
        'osces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('osce_id', sa.String(length=50), nullable=False),
        sa.Column('station_title', sa.String(length=255), nullable=False),
        sa.Column('station_type', postgresql.ENUM(name='oscetype', create_type=False), nullable=False),
        sa.Column('patient_instructions', sa.Text(), nullable=False),
        sa.Column('candidate_instructions', sa.Text(), nullable=False),
        sa.Column('examiner_instructions', sa.Text(), nullable=True),
        sa.Column('rubric', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('specialty', postgresql.ENUM(name='medicalspecialty', create_type=False), nullable=False),
        sa.Column('difficulty', postgresql.ENUM(name='difficultylevel', create_type=False), nullable=False),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=False, server_default='8'),
        sa.Column('learning_objectives', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('key_points', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('red_flags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('australian_guidelines', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('supporting_documents', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('times_practiced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('osce_id')
    )
    op.create_index('ix_osces_id', 'osces', ['id'])
    op.create_index('ix_osces_osce_id', 'osces', ['osce_id'])
    op.create_index('ix_osces_specialty', 'osces', ['specialty'])
    op.create_index('ix_osces_station_type', 'osces', ['station_type'])

    # Create mcq_attempts table
    op.create_table(
        'mcq_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mcq_id', sa.Integer(), nullable=False),
        sa.Column('selected_answer', sa.String(length=1), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=False),
        sa.Column('confidence_level', sa.Integer(), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('was_flagged_for_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['mcq_id'], ['mcqs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_mcq_attempts_user_id', 'mcq_attempts', ['user_id'])
    op.create_index('ix_mcq_attempts_mcq_id', 'mcq_attempts', ['mcq_id'])

    # Create user_progress table
    op.create_table(
        'user_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('specialty', postgresql.ENUM(name='medicalspecialty', create_type=False), nullable=False),
        sa.Column('total_mcqs_attempted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_mcqs_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unique_mcqs_attempted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_osces_practiced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_osce_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('current_streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_study_time_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('weak_topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('mastery_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'specialty', name='unique_user_specialty_progress')
    )
    op.create_index('ix_user_progress_user_id', 'user_progress', ['user_id'])
    op.create_index('ix_user_progress_specialty', 'user_progress', ['specialty'])

    # Create user_favorite_mcqs association table
    op.create_table(
        'user_favorite_mcqs',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mcq_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['mcq_id'], ['mcqs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'mcq_id')
    )

    # Create user_favorite_osces association table
    op.create_table(
        'user_favorite_osces',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('osce_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['osce_id'], ['osces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'osce_id')
    )


def downgrade() -> None:
    """Drop all tables and enum types"""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('user_favorite_osces')
    op.drop_table('user_favorite_mcqs')
    op.drop_table('user_progress')
    op.drop_table('mcq_attempts')
    op.drop_table('osces')
    op.drop_table('mcqs')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE oscetype")
    op.execute("DROP TYPE medicalspecialty")
    op.execute("DROP TYPE difficultylevel")
    op.execute("DROP TYPE userrole")
