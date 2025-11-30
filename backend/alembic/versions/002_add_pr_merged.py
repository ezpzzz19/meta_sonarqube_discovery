"""Add pr_merged column to issues

Revision ID: 002
Revises: 001
Create Date: 2025-11-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add pr_merged column to issues table
    # 0 = not merged (default)
    # 1 = merged (PR was accepted and merged)
    # -1 = unknown/no PR yet
    op.add_column('issues', sa.Column('pr_merged', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('issues', 'pr_merged')
