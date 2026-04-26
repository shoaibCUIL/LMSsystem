"""add course materials and tests tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-26

"""
from alembic import op
import sqlalchemy as sa

revision      = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on    = None


def upgrade():
    op.create_table(
        'course_materials',
        sa.Column('id',           sa.Integer(),     nullable=False),
        sa.Column('course_id',    sa.Integer(),     nullable=False),
        sa.Column('title',        sa.String(200),   nullable=False),
        sa.Column('description',  sa.Text(),        nullable=True),
        sa.Column('file_path',    sa.String(500),   nullable=False),
        sa.Column('file_type',    sa.String(20),    nullable=True),
        sa.Column('file_size_kb', sa.Integer(),     nullable=True),
        sa.Column('order_number', sa.Integer(),     nullable=True),
        sa.Column('is_active',    sa.Boolean(),     nullable=True),
        sa.Column('created_at',   sa.DateTime(),    nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'course_tests',
        sa.Column('id',           sa.Integer(),     nullable=False),
        sa.Column('course_id',    sa.Integer(),     nullable=False),
        sa.Column('title',        sa.String(200),   nullable=False),
        sa.Column('description',  sa.Text(),        nullable=True),
        sa.Column('test_type',    sa.String(20),    nullable=True),
        sa.Column('test_link',    sa.String(500),   nullable=True),
        sa.Column('file_path',    sa.String(500),   nullable=True),
        sa.Column('order_number', sa.Integer(),     nullable=True),
        sa.Column('is_active',    sa.Boolean(),     nullable=True),
        sa.Column('due_date',     sa.DateTime(),    nullable=True),
        sa.Column('created_at',   sa.DateTime(),    nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('course_tests')
    op.drop_table('course_materials')