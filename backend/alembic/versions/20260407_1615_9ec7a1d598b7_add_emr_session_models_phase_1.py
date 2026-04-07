"""Add EMR session models (Phase 1)

Revision ID: 9ec7a1d598b7
Revises: 08a20415c0a1
Create Date: 2026-04-07 16:15:53.589960+10:00

Purpose: Create EMR (Electronic Medical Records) practice system tables
- MockPatient: Simulated patients for EMR training
- EMRSession: EMR practice session tracking
- EMRSOAPNote, EMRPrescription, EMRPathologyOrder: EMR documentation
- EMRValidationResult: AI validation of EMR entries

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '9ec7a1d598b7'
down_revision: Union[str, None] = '20260324_1430'  # Branch from before merge
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing emr_system column to emr_sessions table

    Note: EMR tables already exist in the database (created manually or via SQLAlchemy).
    This migration only adds the missing emr_system column.
    """

    # Add emr_system column to existing emr_sessions table
    op.add_column(
        'emr_sessions',
        sa.Column('emr_system', sa.String(20), nullable=True, comment='"epic" or "cerner"')
    )


def downgrade() -> None:
    """Remove emr_system column from emr_sessions table"""

    # Remove the emr_system column
    op.drop_column('emr_sessions', 'emr_system')
