"""create todos table

Revision ID: 002
Revises: 001
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create todos table with user_id foreign key."""
    op.create_table(
        'todos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create index on user_id for efficient filtering
    op.create_index('ix_todos_user_id', 'todos', ['user_id'], unique=False)

    # Create index on created_at for efficient sorting
    op.create_index('ix_todos_created_at', 'todos', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop todos table and indexes."""
    op.drop_index('ix_todos_created_at', table_name='todos')
    op.drop_index('ix_todos_user_id', table_name='todos')
    op.drop_table('todos')
