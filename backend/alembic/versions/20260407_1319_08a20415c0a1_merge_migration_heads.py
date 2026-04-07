"""Merge migration heads

Revision ID: 08a20415c0a1
Revises: 20260324_1430, 20260405_1841
Create Date: 2026-04-07 13:19:23.452832+10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08a20415c0a1'
down_revision: Union[str, None] = ('20260324_1430', '20260405_1841')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
