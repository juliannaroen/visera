"""add deleted at to users

Revision ID: 52d84137644b
Revises: 3634d43f5c5a
Create Date: 2025-12-03 00:53:55.896065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '52d84137644b'
down_revision: Union[str, None] = '3634d43f5c5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_deleted_at'), table_name='users')
    op.drop_column('users', 'deleted_at')
