"""add learning mode fields to enrollments

Revision ID: b2c3d4e5f6a7
Revises: 793408a0717b
Create Date: 2026-04-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = '793408a0717b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('learning_mode',  sa.String(length=50),  nullable=True))
        batch_op.add_column(sa.Column('preferred_city', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('preferred_days', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('preferred_time', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('schedule_notes', sa.Text(),             nullable=True))


def downgrade():
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.drop_column('schedule_notes')
        batch_op.drop_column('preferred_time')
        batch_op.drop_column('preferred_days')
        batch_op.drop_column('preferred_city')
        batch_op.drop_column('learning_mode')