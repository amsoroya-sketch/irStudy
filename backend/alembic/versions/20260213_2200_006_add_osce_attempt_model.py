"""add osce attempt model

Revision ID: 20260213_2200_006
Revises: 20260213_2000_005
Create Date: 2026-02-13 22:00:00.000000

TASK_002: Question Management CRUD APIs
- Adds OSCEAttempt table for tracking OSCE station completions
- AMC Clinical Exam format: 15-mark rubric (5 categories × 3 marks each)
- Pass mark: 9/15 (60%)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260213_2200_006'
down_revision = '20260213_2000_005'
branch_labels = None
depends_on = None


def upgrade():
    # Create osce_attempts table
    op.create_table(
        'osce_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('osce_id', sa.Integer(), nullable=False),
        sa.Column('scores', sa.JSON(), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=False),
        sa.Column('self_reflection', sa.Text(), nullable=True),
        sa.Column('areas_for_improvement', sa.JSON(), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('was_flagged_for_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['osce_id'], ['osces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('ix_osce_attempts_user_id', 'osce_attempts', ['user_id'])
    op.create_index('ix_osce_attempts_osce_id', 'osce_attempts', ['osce_id'])
    op.create_index('ix_osce_attempts_attempted_at', 'osce_attempts', ['attempted_at'])

    # Add comment to table
    op.execute("""
        COMMENT ON TABLE osce_attempts IS 'OSCE station practice attempts with AMC 15-mark rubric scoring';
    """)


def downgrade():
    op.drop_index('ix_osce_attempts_attempted_at', table_name='osce_attempts')
    op.drop_index('ix_osce_attempts_osce_id', table_name='osce_attempts')
    op.drop_index('ix_osce_attempts_user_id', table_name='osce_attempts')
    op.drop_table('osce_attempts')
