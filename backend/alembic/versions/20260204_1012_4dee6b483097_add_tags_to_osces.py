"""add_tags_to_osces

Revision ID: 4dee6b483097
Revises: 001
Create Date: 2026-02-04 10:12:24.281608+11:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4dee6b483097'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add tags column to osces table for filtering and categorization"""
    op.add_column('osces',
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )


def downgrade() -> None:
    """Remove tags column from osces table"""
    op.drop_column('osces', 'tags')
