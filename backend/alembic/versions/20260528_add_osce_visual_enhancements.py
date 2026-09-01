"""Add OSCE visual enhancements and study notes

Revision ID: 20260528_visual_enhancements
Revises: 20260527_mcq_quality
Create Date: 2026-05-28

DESCRIPTION:
    Adds support for educational images and study notes for OSCEs:
    - educational_images: JSONB column for storing generated educational images
    - dr_amir_format: Boolean flag for Dr. Amir enhanced OSCEs
    - osce_study_notes: New table for linking study notes to OSCEs

CONTEXT:
    Phase 1 of 8-week UI enhancement plan for displaying Dr. Amir OSCE content.
    Supports programmatic image generation using Python libraries (matplotlib, seaborn, graphviz).

RELATED:
    - UI_DISPLAY_MASTER_LIST.md (complete content inventory)
    - COMPLETE_UI_UX_MASTER_PLAN.md (comprehensive UI specifications)
    - Week 1-2: Foundation & Database phase
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20260528_visual_enhancements'
down_revision = '9ec7a1d598b7'  # Points to 20260407_1615_9ec7a1d598b7_add_emr_session_models_phase_1.py
branch_labels = None
depends_on = None


def upgrade():
    """
    Add OSCE visual enhancements support.

    CHANGES:
    1. osces.educational_images: JSONB for storing image metadata
       Example structure:
       {
         "comparison_charts": [{
           "title": "Gastric vs Duodenal Ulcer",
           "image_url": "/static/images/osces/GI-PUD-001_gastric_duodenal_comparison.png",
           "type": "comparison_table",
           "generated_at": "2026-05-28T10:30:00Z"
         }],
         "decision_trees": [{
           "title": "Red Flag Assessment",
           "image_url": "/static/images/osces/GI-PUD-001_red_flag_decision_tree.png",
           "type": "decision_tree"
         }],
         "timelines": [{
           "title": "Pain Timing After Meals",
           "image_url": "/static/images/osces/GI-PUD-001_pain_timing.png",
           "type": "timeline"
         }],
         "flowcharts": [{
           "title": "Management Pathway",
           "image_url": "/static/images/osces/GI-PUD-001_management_pathway.png",
           "type": "flowchart"
         }]
       }

    2. osces.dr_amir_format: Boolean flag (default: False)
       True = OSCE uses Dr. Amir's 5 Ps Framework (724-line enhanced format)
       False = Standard OSCE format

    3. osce_study_notes: New table for study notes
       Links study notes (from /ICRP_OSCE_Preparation/) to OSCEs
       Supports markdown content, tags, topics, and cross-referencing
    """

    # 1. Add educational_images JSONB column to osces table
    op.add_column('osces', sa.Column('educational_images', postgresql.JSONB, nullable=True))

    print("✅ Added osces.educational_images (JSONB) - stores image metadata")

    # 2. Add dr_amir_format Boolean column to osces table
    op.add_column('osces', sa.Column('dr_amir_format', sa.Boolean(), nullable=False, server_default='false'))

    print("✅ Added osces.dr_amir_format (Boolean) - flags Dr. Amir enhanced OSCEs")

    # 3. Create osce_study_notes table
    op.create_table(
        'osce_study_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.String(50), nullable=False),  # e.g., "STUDY-CARD-001"
        sa.Column('osce_id', sa.Integer(), sa.ForeignKey('osces.id', ondelete='CASCADE'), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content_markdown', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('reading_time_minutes', sa.Integer(), nullable=True),
        sa.Column('topics', postgresql.JSONB, nullable=True),  # ["Peptic Ulcer Disease", "Gastroenterology"]
        sa.Column('tags', postgresql.JSONB, nullable=True),  # ["red_flags", "management", "differential_diagnosis"]
        sa.Column('amc_relevance', sa.String(50), nullable=True),  # "high", "medium", "low"
        sa.Column('specialty', sa.String(100), nullable=True),  # "Medicine", "Surgery", "Psychiatry"
        sa.Column('related_osce_ids', postgresql.JSONB, nullable=True),  # [1, 5, 12] - related OSCE IDs
        sa.Column('related_mcq_ids', postgresql.JSONB, nullable=True),  # [45, 67, 89] - related MCQ IDs
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for osce_study_notes
    op.create_index('ix_osce_study_notes_note_id', 'osce_study_notes', ['note_id'], unique=True)
    op.create_index('ix_osce_study_notes_osce_id', 'osce_study_notes', ['osce_id'])
    op.create_index('ix_osce_study_notes_specialty', 'osce_study_notes', ['specialty'])
    op.create_index('ix_osce_study_notes_amc_relevance', 'osce_study_notes', ['amc_relevance'])

    print("✅ Created osce_study_notes table with 4 indexes")
    print("   - Stores 106 study notes from /ICRP_OSCE_Preparation/")
    print("   - Links to OSCEs, MCQs for cross-referencing")
    print("   - Supports markdown content, tags, topics")

    print("\n🎯 Week 1-2 Database Foundation COMPLETE")
    print("   Next: Set up Python image generation environment")


def downgrade():
    """
    Remove OSCE visual enhancements.

    WARNING: This will delete all educational image metadata and study notes.
    Only use for rollback in emergency situations.
    """

    # Drop osce_study_notes table (cascade will remove all notes)
    op.drop_index('ix_osce_study_notes_amc_relevance', table_name='osce_study_notes')
    op.drop_index('ix_osce_study_notes_specialty', table_name='osce_study_notes')
    op.drop_index('ix_osce_study_notes_osce_id', table_name='osce_study_notes')
    op.drop_index('ix_osce_study_notes_note_id', table_name='osce_study_notes')
    op.drop_table('osce_study_notes')

    # Remove columns from osces table
    op.drop_column('osces', 'dr_amir_format')
    op.drop_column('osces', 'educational_images')

    print("⚠️  WARNING: Removed OSCE visual enhancements")
    print("   - Deleted all educational image metadata")
    print("   - Deleted all study notes")
    print("   - This should only be used for emergency rollback")
