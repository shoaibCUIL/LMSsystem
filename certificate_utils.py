"""add completion fields to enrollments

Revision ID: add_completion_fields
Revises: 
Create Date: 2026-04-24

Run with: flask db upgrade
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('enrollments',
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='0')
    )
    op.add_column('enrollments',
        sa.Column('completed_at', sa.DateTime(), nullable=True)
    )
    op.add_column('enrollments',
        sa.Column('certificate_id', sa.String(64), nullable=True)
    )


def downgrade():
    op.drop_column('enrollments', 'is_completed')
    op.drop_column('enrollments', 'completed_at')
    op.drop_column('enrollments', 'certificate_id')