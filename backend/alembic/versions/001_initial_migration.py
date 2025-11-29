"""Initial migration - create issues and events tables

Revision ID: 001
Revises: 
Create Date: 2025-11-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create issues table
    op.create_table(
        'issues',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('sonarqube_issue_key', sa.String(255), nullable=False),
        sa.Column('project_key', sa.String(255), nullable=False),
        sa.Column('rule', sa.String(255), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('component', sa.String(500), nullable=False),
        sa.Column('line', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum(
            'NEW', 'FIXING', 'PR_OPEN', 'CI_PASSED', 'CI_FAILED', 'CLOSED',
            name='issuestatus'
        ), nullable=False),
        sa.Column('pr_url', sa.String(500), nullable=True),
        sa.Column('pr_branch', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for issues table
    op.create_index('ix_issues_sonarqube_issue_key', 'issues', ['sonarqube_issue_key'], unique=True)
    op.create_index('ix_issues_project_key', 'issues', ['project_key'])
    op.create_index('ix_issues_status', 'issues', ['status'])
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('issue_id', UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.Enum(
            'ISSUE_DETECTED', 'AI_CALLED', 'PR_CREATED', 'CI_PASSED', 'CI_FAILED', 'STATUS_UPDATED', 'ERROR',
            name='eventtype'
        ), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('event_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for events table
    op.create_index('ix_events_issue_id', 'events', ['issue_id'])
    op.create_index('ix_events_event_type', 'events', ['event_type'])
    op.create_index('ix_events_created_at', 'events', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_events_created_at', table_name='events')
    op.drop_index('ix_events_event_type', table_name='events')
    op.drop_index('ix_events_issue_id', table_name='events')
    op.drop_index('ix_issues_status', table_name='issues')
    op.drop_index('ix_issues_project_key', table_name='issues')
    op.drop_index('ix_issues_sonarqube_issue_key', table_name='issues')
    
    # Drop tables
    op.drop_table('events')
    op.drop_table('issues')
    
    # Drop enums
    op.execute('DROP TYPE eventtype')
    op.execute('DROP TYPE issuestatus')
