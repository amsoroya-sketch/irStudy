"""add_emr_phase4_tables

Revision ID: 797dec28db20
Revises: 2accee07a21b
Create Date: 2026-03-21 22:29:48.033619+11:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '797dec28db20'
down_revision: Union[str, None] = '2accee07a21b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
