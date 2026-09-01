"""Add HTML OSCE notes table

Revision ID: 20260528_1800_html_notes
Revises: 20260528_visual_enhancements
Create Date: 2026-05-28 18:00

DESCRIPTION:
    Adds table for tracking pre-generated HTML OSCE notes
    - 65 HTML files in /ICRP_OSCE_Preparation/
    - Organized by specialty (Medicine, Surgery, Psychiatry, etc.)
    - Uses Dr. Amir's method with embedded CSS

CONTEXT:
    User has existing HTML notes that need to be listed in app
    These are separate from markdown study notes
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20260528_1800_html_notes'
down_revision = '20260528_visual_enhancements'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create html_osce_notes table.

    Stores metadata for pre-generated HTML OSCE notes files.
    Files are served as static content, not stored in database.
    """
    op.create_table(
        'html_osce_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.String(50), nullable=False),  # e.g., "HTML-MED-001"
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),  # Relative path from ICRP_OSCE_Preparation/
        sa.Column('specialty', sa.String(100), nullable=False),  # Medicine, Surgery, Psychiatry, etc.
        sa.Column('category', sa.String(100), nullable=True),  # History, Physical Exam, Emergency, etc.
        sa.Column('topics', postgresql.JSONB, nullable=True),  # Extracted topics
        sa.Column('preview_text', sa.Text(), nullable=True),  # First 200 chars for preview
        sa.Column('file_size_kb', sa.Integer(), nullable=True),
        sa.Column('estimated_reading_minutes', sa.Integer(), nullable=True),
        sa.Column('related_osce_ids', postgresql.JSONB, nullable=True),  # Link to osces table
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_html_osce_notes_note_id', 'html_osce_notes', ['note_id'], unique=True)
    op.create_index('ix_html_osce_notes_specialty', 'html_osce_notes', ['specialty'])
    op.create_index('ix_html_osce_notes_category', 'html_osce_notes', ['category'])

    print("✅ Created html_osce_notes table with 3 indexes")
    print("   - Tracks 65 HTML OSCE notes from /ICRP_OSCE_Preparation/")
    print("   - Files served as static content")
    print("   - Organized by specialty and category")


def downgrade():
    """Remove html_osce_notes table"""
    op.drop_index('ix_html_osce_notes_category', table_name='html_osce_notes')
    op.drop_index('ix_html_osce_notes_specialty', table_name='html_osce_notes')
    op.drop_index('ix_html_osce_notes_note_id', table_name='html_osce_notes')
    op.drop_table('html_osce_notes')

    print("⚠️  WARNING: Removed html_osce_notes table")
