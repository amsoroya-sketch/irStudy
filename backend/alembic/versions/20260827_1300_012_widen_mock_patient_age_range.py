"""Widen mock_patients age range to support paediatric EMR cases

Revision ID: 20260827_1300_012
Revises: 20260827_1200_011
Create Date: 2026-08-27 13:00:00

PRD-EMR-PRACTICE-002.

Purpose:
- The original `check_mock_patients_age_range` constraint (age >= 18 AND
  age <= 100, from migration 008) rejects clinically valid paediatric cases.
  For example, testicular torsion at age 16 is the canonical presentation, and
  the platform plans paediatric EMR practice cases.
- This migration widens the range to age >= 0 AND age <= 120 so paediatric
  (and very elderly) cases can be imported into `mock_patients`.

Downgrade restores the original adult-only bounds (age >= 18 AND age <= 100).
"""

from alembic import op

# Revision identifiers
revision = '20260827_1300_012'
down_revision = '20260827_1200_011'
branch_labels = None
depends_on = None

_CONSTRAINT = 'check_mock_patients_age_range'
_TABLE = 'mock_patients'
_WIDE = 'age >= 0 AND age <= 120'
_ORIGINAL = 'age >= 18 AND age <= 100'


def upgrade() -> None:
    op.drop_constraint(_CONSTRAINT, _TABLE, type_='check')
    op.create_check_constraint(_CONSTRAINT, _TABLE, _WIDE)


def downgrade() -> None:
    op.drop_constraint(_CONSTRAINT, _TABLE, type_='check')
    op.create_check_constraint(_CONSTRAINT, _TABLE, _ORIGINAL)
