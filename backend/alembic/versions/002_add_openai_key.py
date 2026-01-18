"""Add encrypted OpenAI API key to users

Revision ID: 002_add_openai_key
Revises: 001_initial
Create Date: 2026-01-18

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_openai_key'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('encrypted_openai_key', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'encrypted_openai_key')
