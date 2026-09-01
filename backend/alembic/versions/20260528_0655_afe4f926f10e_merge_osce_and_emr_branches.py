"""merge_osce_and_emr_branches

Revision ID: afe4f926f10e
Revises: 20260405_1841, 20260528_1800_html_notes
Create Date: 2026-05-28 06:55:15.263541+10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afe4f926f10e'
down_revision: Union[str, None] = ('20260405_1841', '20260528_1800_html_notes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
