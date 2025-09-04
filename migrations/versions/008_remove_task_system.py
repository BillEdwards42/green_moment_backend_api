"""Remove task system

Revision ID: 008
Revises: 007
Create Date: 2025-08-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Drop foreign key constraints first
    op.drop_constraint('user_tasks_user_id_fkey', 'user_tasks', type_='foreignkey')
    op.drop_constraint('user_tasks_task_id_fkey', 'user_tasks', type_='foreignkey')
    
    # Drop tables
    op.drop_table('user_tasks')
    op.drop_table('tasks')
    
    # Drop columns from users table
    op.drop_column('users', 'current_month_tasks_completed')
    
    # Drop columns from monthly_summaries table
    op.drop_column('monthly_summaries', 'tasks_completed')
    op.drop_column('monthly_summaries', 'total_points_earned')


def downgrade():
    # Re-create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('league', sa.String(), nullable=False),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('target_value', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    
    # Re-create user_tasks table
    op.create_table('user_tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('points_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_tasks_id'), 'user_tasks', ['id'], unique=False)
    
    # Re-add columns to users table
    op.add_column('users', sa.Column('current_month_tasks_completed', sa.Integer(), nullable=False, server_default='0'))
    
    # Re-add columns to monthly_summaries table
    op.add_column('monthly_summaries', sa.Column('tasks_completed', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('monthly_summaries', sa.Column('total_points_earned', sa.Integer(), nullable=False, server_default='0'))