"""Add structured MCQ.citations JSON column

Revision ID: 20260902_1000_014
Revises: 20260901_1000_013
Create Date: 2026-09-02 10:00:00

PRD-MCQ-CITATION-001.

Purpose:
- Add a nullable ``citations`` JSON column to ``mcqs``, mirroring
  ``StudyCard.citations`` (models.py:1316). Each element is a structured
  citation object ({source, qdrant_point_id, confidence, is_australian,
  title, author, year, page}) so MCQ references can carry a verifiable
  ``qdrant_point_id`` instead of the flat ``citation`` summary string.
- The existing ``citation`` String(500) column is left untouched — it
  keeps serving as the human-readable summary of the primary citation.

Additive + fully reversible: ``downgrade`` drops the column, leaving the
schema exactly as before. No backfill happens in this migration — backfill
is performed by ``scripts/remediate_mcq_citations.py``.
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '20260902_1000_014'
down_revision = '20260901_1000_013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('mcqs', sa.Column('citations', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('mcqs', 'citations')
