"""Add study cards table

Revision ID: 002
Revises: 001
Create Date: 2026-02-07 08:05:00

TABLES:
- study_cards: Study cards for spaced repetition learning

FEATURES:
- SM-2 algorithm support (ease_factor, interval_days, repetitions)
- Australian medical context (citations, specialty, difficulty)
- User-specific and shared/public cards (nullable user_id)
- Soft deletes for audit compliance
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "002"
down_revision: Union[str, None] = "4dee6b483097"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create study_cards table"""

    # Create study_cards table
    op.create_table(
        "study_cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("card_id", sa.String(length=50), nullable=False),
        sa.Column(
            "specialty",
            postgresql.ENUM(name="medicalspecialty", create_type=False),
            nullable=False,
        ),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("subtopic", sa.String(length=255), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("citations", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "difficulty",
            postgresql.ENUM(name="difficultylevel", create_type=False),
            nullable=False,
            server_default="medium",
        ),
        sa.Column("tags", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("card_type", sa.String(length=50), nullable=False, server_default="concept"),
        sa.Column(
            "next_review_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("card_id"),
    )

    # Create indexes for performance
    op.create_index("ix_study_cards_id", "study_cards", ["id"])
    op.create_index("ix_study_cards_card_id", "study_cards", ["card_id"], unique=True)
    op.create_index("ix_study_cards_user_id", "study_cards", ["user_id"])
    op.create_index("ix_study_cards_specialty", "study_cards", ["specialty"])
    op.create_index("ix_study_cards_topic", "study_cards", ["topic"])
    op.create_index("ix_study_cards_difficulty", "study_cards", ["difficulty"])
    op.create_index("ix_study_cards_next_review_date", "study_cards", ["next_review_date"])

    # Composite index for spaced repetition queries (user + review date)
    op.create_index(
        "ix_study_cards_user_next_review",
        "study_cards",
        ["user_id", "next_review_date"],
    )

    # Composite index for filtering by specialty and difficulty
    op.create_index(
        "ix_study_cards_specialty_difficulty",
        "study_cards",
        ["specialty", "difficulty"],
    )


def downgrade() -> None:
    """Drop study_cards table and indexes"""

    # Drop indexes
    op.drop_index("ix_study_cards_specialty_difficulty", table_name="study_cards")
    op.drop_index("ix_study_cards_user_next_review", table_name="study_cards")
    op.drop_index("ix_study_cards_next_review_date", table_name="study_cards")
    op.drop_index("ix_study_cards_difficulty", table_name="study_cards")
    op.drop_index("ix_study_cards_topic", table_name="study_cards")
    op.drop_index("ix_study_cards_specialty", table_name="study_cards")
    op.drop_index("ix_study_cards_user_id", table_name="study_cards")
    op.drop_index("ix_study_cards_card_id", table_name="study_cards")
    op.drop_index("ix_study_cards_id", table_name="study_cards")

    # Drop table
    op.drop_table("study_cards")
