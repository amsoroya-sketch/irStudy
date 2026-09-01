"""Add AMC conditions/blueprint spine + nullable condition_id FKs

Revision ID: 20260901_1000_013
Revises: 20260827_1300_012
Create Date: 2026-09-01 10:00:00

PRD-CONDITIONS-SPINE-001.

Purpose:
- Create the ``conditions`` table: a single, joinable anchor for AMC
  conditions / blueprint areas. Rows are derived deterministically from
  existing content topics (no LLM) by ``scripts/seed_conditions.py``.
- Add a nullable ``condition_id`` FK (ON DELETE SET NULL) to the four content
  tables — ``mcqs``, ``osces``, ``patient_personas``, ``mock_patients`` — so
  every content row can be anchored to a condition/blueprint area.

Additive + fully reversible: ``downgrade`` drops the FKs then the table,
leaving the schema exactly as before. The existing ``medicalspecialty``
PostgreSQL enum type is REUSED (create_type=False) — this migration never
creates or drops that type.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '20260901_1000_013'
down_revision = '20260827_1300_012'
branch_labels = None
depends_on = None


# The four content tables that receive a nullable condition_id FK.
_CONTENT_TABLES = ('mcqs', 'osces', 'patient_personas', 'mock_patients')


def _specialty_enum():
    """Reuse the existing medicalspecialty PG enum; plain enum on other backends."""
    return postgresql.ENUM(name='medicalspecialty', create_type=False)


def upgrade() -> None:
    # 1) conditions table
    op.create_table(
        'conditions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('condition_code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('specialty', _specialty_enum(), nullable=False),
        sa.Column('amc_blueprint_area', sa.String(length=100), nullable=False),
        sa.Column('aliases', sa.JSON(), nullable=True),
        sa.Column('system', sa.String(length=100), nullable=True),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.text('now()'), nullable=False,
        ),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True),
            server_default=sa.text('now()'), nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_conditions_id', 'conditions', ['id'])
    op.create_index('ix_conditions_condition_code', 'conditions', ['condition_code'], unique=True)
    op.create_index('ix_conditions_name', 'conditions', ['name'])
    op.create_index('ix_conditions_specialty', 'conditions', ['specialty'])
    op.create_index('ix_conditions_amc_blueprint_area', 'conditions', ['amc_blueprint_area'])

    # 2) nullable condition_id FK on each content table (ON DELETE SET NULL)
    for table in _CONTENT_TABLES:
        op.add_column(table, sa.Column('condition_id', sa.Integer(), nullable=True))
        op.create_index(f'ix_{table}_condition_id', table, ['condition_id'])
        op.create_foreign_key(
            f'fk_{table}_condition_id',
            table,
            'conditions',
            ['condition_id'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    # Reverse order: drop FKs + columns, then indexes, then the table.
    for table in _CONTENT_TABLES:
        op.drop_constraint(f'fk_{table}_condition_id', table, type_='foreignkey')
        op.drop_index(f'ix_{table}_condition_id', table_name=table)
        op.drop_column(table, 'condition_id')

    op.drop_index('ix_conditions_amc_blueprint_area', table_name='conditions')
    op.drop_index('ix_conditions_specialty', table_name='conditions')
    op.drop_index('ix_conditions_name', table_name='conditions')
    op.drop_index('ix_conditions_condition_code', table_name='conditions')
    op.drop_index('ix_conditions_id', table_name='conditions')
    op.drop_table('conditions')
