"""Add Google OAuth support to users

Revision ID: 003_add_google_oauth
Revises: 002_add_openai_key
Create Date: 2026-01-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_add_google_oauth'
down_revision: Union[str, None] = '002_add_openai_key'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add google_id column for Google OAuth users
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])

    # Make hashed_password nullable for Google OAuth users
    op.alter_column('users', 'hashed_password', nullable=True)


def downgrade() -> None:
    op.alter_column('users', 'hashed_password', nullable=False)
    op.drop_constraint('uq_users_google_id', 'users', type_='unique')
    op.drop_column('users', 'google_id')
