"""add_is_email_verified_to_users

Revision ID: 07d7e8739bbf
Revises: 796debcfa78c
Create Date: 2025-11-28 14:43:20.708111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07d7e8739bbf'
down_revision: Union[str, None] = '796debcfa78c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the column with server_default='false'
    # This will automatically set all existing rows to False and set default for new rows
    op.add_column('users',
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )


def downgrade() -> None:
    # Remove the column
    op.drop_column('users', 'is_email_verified')

