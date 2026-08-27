"""Map MockPatient answer-key columns (verify) + merge heads

Revision ID: 20260827_1200_011
Revises: 20260825_workshop_specialties, 20260215_1600_010, 20260528_1800_html_notes
Create Date: 2026-08-27 12:00:00

PRD-EMR-PRACTICE-001.

Purpose:
- The MockPatient answer-key / clinical-detail columns (validation_criteria,
  demographics, medications, allergies, physical_exam_findings,
  investigation_results, source_osce_id) were already created by migration 008.
  They were unmapped in the ORM until this PRD. This migration is an idempotent
  VERIFY step (ADD COLUMN IF NOT EXISTS) so fresh databases are guaranteed to
  carry them; it is a no-op on databases that already ran 008.
- It also merges the three pre-existing alembic heads into one so
  `alembic upgrade head` resolves cleanly.
"""

from alembic import op

# Revision identifiers
revision = '20260827_1200_011'
down_revision = (
    '20260825_workshop_specialties',
    '20260215_1600_010',
    '20260528_1800_html_notes',
)
branch_labels = None
depends_on = None


# Columns that must exist on mock_patients for the assessment engine.
_JSON_COLUMNS = [
    'demographics',
    'medications',
    'allergies',
    'physical_exam_findings',
    'investigation_results',
    'validation_criteria',
]


def upgrade():
    """Idempotently ensure MockPatient answer-key columns exist."""
    bind = op.get_bind()
    # Guard for non-PostgreSQL backends (e.g. SQLite in tests) which do not
    # support `ADD COLUMN IF NOT EXISTS`; there the ORM metadata creates the
    # columns directly, so this migration is a no-op.
    if bind.dialect.name != 'postgresql':
        return

    for col in _JSON_COLUMNS:
        op.execute(
            f'ALTER TABLE mock_patients ADD COLUMN IF NOT EXISTS {col} JSON'
        )
    op.execute(
        'ALTER TABLE mock_patients ADD COLUMN IF NOT EXISTS source_osce_id INTEGER'
    )


def downgrade():
    """No-op: these columns are owned by migration 008; do not drop them here."""
    pass
