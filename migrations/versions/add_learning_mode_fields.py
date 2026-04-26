"""add learning mode fields to enrollments

Revision ID: add_learning_mode_fields
Revises: 793408a0717b
Create Date: 2026-04-26

Run with: flask db upgrade
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('learning_mode',   sa.String(50),  nullable=True))
        batch_op.add_column(sa.Column('preferred_city',  sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('preferred_days',  sa.String(200), nullable=True))
        batch_op.add_column(sa.Column('preferred_time',  sa.String(200), nullable=True))
        batch_op.add_column(sa.Column('schedule_notes',  sa.Text(),      nullable=True))


def downgrade():
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.drop_column('schedule_notes')
        batch_op.drop_column('preferred_time')
        batch_op.drop_column('preferred_days')
        batch_op.drop_column('preferred_city')
        batch_op.drop_column('learning_mode')