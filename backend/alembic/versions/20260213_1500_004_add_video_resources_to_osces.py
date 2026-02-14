"""add video resources to osces

Revision ID: 20260213_1500_004
Revises: 003
Create Date: 2026-02-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '20260213_1500_004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add video_resources JSON field to osces table.

    Structure:
    {
        "essential_videos": [
            {
                "title": "Cardiovascular Examination - Stanford Medicine 25",
                "url": "https://stanfordmedicine25.stanford.edu/the25/cardiovascular.html",
                "source": "Stanford Medicine 25",
                "duration_minutes": 10,
                "focus": "Complete systematic cardiac examination",
                "why_recommended": "Gold standard demonstration from Stanford"
            }
        ],
        "supplementary_videos": [...]
    }
    """
    # Add video_resources column to osces table
    op.add_column(
        'osces',
        sa.Column('video_resources', JSON, nullable=True)
    )


def downgrade() -> None:
    """Remove video_resources field from osces table"""
    op.drop_column('osces', 'video_resources')
