"""Add email verification and password reset fields

Revision ID: 003
Revises: 002
Create Date: 2026-02-07 14:00:00

FIELDS ADDED:
- verification_token: Email verification token (String(255), unique)
- verification_token_created_at: Token creation timestamp
- reset_token: Password reset token (String(255), unique)
- reset_token_created_at: Token creation timestamp

SECURITY:
- Tokens are nullable (only set when needed)
- Unique indexes for fast lookup
- Timestamps for expiration checking (24h verification, 1h reset)
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add verification and reset token fields to users table"""
    
    # Add email verification fields
    op.add_column('users', sa.Column('verification_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('verification_token_created_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add password reset fields
    op.add_column('users', sa.Column('reset_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('reset_token_created_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create unique indexes for token lookup
    op.create_index('ix_users_verification_token', 'users', ['verification_token'], unique=True)
    op.create_index('ix_users_reset_token', 'users', ['reset_token'], unique=True)


def downgrade() -> None:
    """Remove verification and reset token fields from users table"""
    
    # Drop indexes first
    op.drop_index('ix_users_reset_token', table_name='users')
    op.drop_index('ix_users_verification_token', table_name='users')
    
    # Drop columns
    op.drop_column('users', 'reset_token_created_at')
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'verification_token_created_at')
    op.drop_column('users', 'verification_token')
