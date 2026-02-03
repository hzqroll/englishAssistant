"""add_llm_provider_tables

Revision ID: d24290d4e5c8
Revises: 474a3ca52c69
Create Date: 2026-02-03 17:16:19.889362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd24290d4e5c8'
down_revision: Union[str, Sequence[str], None] = '474a3ca52c69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ea_llm_providers table
    op.create_table(
        'ea_llm_providers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('default_api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('supported_models', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_llm_provider_name')
    )

    # Create ea_user_llm_configs table
    op.create_table(
        'ea_user_llm_configs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('provider_name', sa.String(length=50), nullable=False),
        sa.Column('selected_model', sa.String(length=100), nullable=False),
        sa.Column('custom_api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['ea_users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'provider_name', name='uq_user_provider')
    )

    # Add LLM configuration columns to ea_user_settings
    op.add_column('ea_user_settings', sa.Column('active_llm_provider', sa.String(length=50), nullable=False, server_default='zhipu'))
    op.add_column('ea_user_settings', sa.Column('active_llm_model', sa.String(length=100), nullable=False, server_default='glm-4-flashx'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns from ea_user_settings
    op.drop_column('ea_user_settings', 'active_llm_model')
    op.drop_column('ea_user_settings', 'active_llm_provider')

    # Drop tables
    op.drop_table('ea_user_llm_configs')
    op.drop_table('ea_llm_providers')
