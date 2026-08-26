"""Add ophthalmology, urology, musculoskeletal to medicalspecialty enum

New Dr. Amir workshop content (25-august-docs) covers ophthalmology, urology and
MSK cases; the medicalspecialty enum previously had no values for them, which
would silently block imports (same failure class as the May 2026 OSCEType
COMMUNICATION_SKILLS incident).

Revision ID: 20260825_workshop_specialties
Revises: afe4f926f10e
Create Date: 2026-08-25
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260825_workshop_specialties"
down_revision = "afe4f926f10e"
branch_labels = None
depends_on = None

NEW_VALUES = ["ophthalmology", "urology", "musculoskeletal"]


def upgrade():
    for value in NEW_VALUES:
        op.execute(f"ALTER TYPE medicalspecialty ADD VALUE IF NOT EXISTS '{value}'")


def downgrade():
    # PostgreSQL cannot remove enum values in place; recreating the type would
    # require rewriting every dependent column. Intentionally a no-op — the
    # extra values are harmless if unused.
    pass
