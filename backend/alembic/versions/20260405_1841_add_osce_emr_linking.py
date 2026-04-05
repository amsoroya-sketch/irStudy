"""add_osce_emr_linking

Revision ID: 20260405_1841
Revises: 797dec28db20
Create Date: 2026-04-05 18:41:00.000000+11:00

Purpose: Enable OSCE-to-EMR conversion integration
- Links EMR sessions to source OSCE attempts
- Stores conversion metadata (pre-fill %, confidence scores)
- Enables pedagogical learning transfer tracking

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = '20260405_1841'
down_revision: Union[str, None] = '797dec28db20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add OSCE-to-EMR linking columns to emr_sessions table

    New columns:
    - source_osce_attempt_id: Foreign key to osce_attempts_ai (nullable)
    - conversion_metadata: JSONB storing conversion metrics

    Indexes:
    - idx_emr_sessions_osce_source: For reverse lookup (find EMR from OSCE)
    """

    # Add source_osce_attempt_id column (links to AI OSCE attempts)
    op.add_column(
        'emr_sessions',
        sa.Column(
            'source_osce_attempt_id',
            UUID(as_uuid=True),
            nullable=True,
            comment='Source OSCE attempt that generated this EMR session (null for manual creation)'
        )
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_emr_sessions_osce_source',
        'emr_sessions',
        'osce_attempts_ai',
        ['source_osce_attempt_id'],
        ['attempt_id'],
        ondelete='SET NULL'  # Preserve EMR session if OSCE deleted
    )

    # Add conversion_metadata column (JSONB for flexibility)
    op.add_column(
        'emr_sessions',
        sa.Column(
            'conversion_metadata',
            JSONB,
            nullable=True,
            comment='Conversion metrics: pre_fill_percentage, extraction_confidence, tokens_used, etc.'
        )
    )

    # Create index for reverse lookup (find EMR sessions generated from OSCE)
    op.create_index(
        'idx_emr_sessions_osce_source',
        'emr_sessions',
        ['source_osce_attempt_id']
    )

    # Create partial index for non-null OSCE sources (faster filtering)
    op.create_index(
        'idx_emr_sessions_osce_converted',
        'emr_sessions',
        ['source_osce_attempt_id'],
        postgresql_where=sa.text('source_osce_attempt_id IS NOT NULL')
    )


def downgrade() -> None:
    """
    Remove OSCE-to-EMR linking (rollback)
    """
    # Drop indexes first
    op.drop_index('idx_emr_sessions_osce_converted', table_name='emr_sessions')
    op.drop_index('idx_emr_sessions_osce_source', table_name='emr_sessions')

    # Drop foreign key constraint
    op.drop_constraint('fk_emr_sessions_osce_source', 'emr_sessions', type_='foreignkey')

    # Drop columns
    op.drop_column('emr_sessions', 'conversion_metadata')
    op.drop_column('emr_sessions', 'source_osce_attempt_id')
