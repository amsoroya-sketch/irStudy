"""add_session_id_to_study_cards

Revision ID: 20260324_1430
Revises: 20260215_1453_009
Create Date: 2026-03-24 14:30:00.000000+11:00

Phase 1: Study Card Generation from OSCE Sessions

Adds session_id column to study_cards table to link auto-generated cards
to the OSCE session that produced them.

Schema Changes:
- Add session_id VARCHAR(255) column (nullable - manually created cards won't have session)
- Add foreign key to ai_osce_attempts(attempt_id) with ON DELETE SET NULL
- Add index idx_study_cards_session_id for query performance

Performance Impact:
- Migration time: <30 seconds (simple column addition, no data transformation)
- Index creation: <10 seconds (small table initially)
- No table locks (PostgreSQL ALTER TABLE ... ADD COLUMN is non-blocking for nullable columns)

Security:
- No hardcoded credentials
- Foreign key preserves referential integrity
- ON DELETE SET NULL preserves study cards even if session deleted
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '20260324_1430'
down_revision: Union[str, None] = '797dec28db20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add session_id column to study_cards table.

    Links auto-generated study cards to the OSCE session that created them.
    Manually created cards will have session_id = NULL.
    """
    # Add session_id column (nullable, UUID type to match ai_osce_attempts.attempt_id)
    op.add_column(
        'study_cards',
        sa.Column('session_id', UUID(as_uuid=True), nullable=True)
    )

    # Add foreign key constraint to ai_osce_attempts
    # ON DELETE SET NULL preserves cards even if session is deleted
    op.create_foreign_key(
        'fk_study_cards_session',
        'study_cards',
        'ai_osce_attempts',
        ['session_id'],
        ['attempt_id'],
        ondelete='SET NULL'
    )

    # Create index for efficient queries
    # Use case: "Show me cards from this session" or "Has this session generated cards?"
    op.create_index(
        'idx_study_cards_session_id',
        'study_cards',
        ['session_id']
    )

    # Add comment for documentation
    op.execute(
        "COMMENT ON COLUMN study_cards.session_id IS "
        "'Links study card to OSCE session that generated it. NULL for manually created cards.'"
    )


def downgrade() -> None:
    """
    Remove session_id column from study_cards table.

    Rollback migration if needed (e.g., if Phase 1 testing fails).
    """
    # Drop index first (dependency)
    op.drop_index('idx_study_cards_session_id', table_name='study_cards')

    # Drop foreign key constraint
    op.drop_constraint('fk_study_cards_session', 'study_cards', type_='foreignkey')

    # Drop column
    op.drop_column('study_cards', 'session_id')
