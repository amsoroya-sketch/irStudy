"""Add structured PatientPersona.citations JSON column

Revision ID: 20260920_1000_015
Revises: 20260902_1000_014
Create Date: 2026-09-20 10:00:00

PRD-PERSONA-CITATION-001.

Purpose:
- Add a nullable ``citations`` JSON column to ``patient_personas``, mirroring
  ``MCQ.citations`` (models.py:362) and ``StudyCard.citations``. Each element
  is a structured citation object ({source, qdrant_point_id, confidence,
  is_australian, title, ...}) so each persona's RAG grounding (the 5 point-ids
  produced during generation) can be persisted and queried, instead of being
  discarded on import.
- All other persona columns are left untouched.

Additive + fully reversible: ``downgrade`` drops the column, leaving the
schema exactly as before. No backfill happens in this migration — backfill of
the 48 already-imported grounded personas is performed by re-running
``scripts/import_patient_personas.py`` (which updates null citations in place).
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '20260920_1000_015'
down_revision = '20260902_1000_014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('patient_personas', sa.Column('citations', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('patient_personas', 'citations')
