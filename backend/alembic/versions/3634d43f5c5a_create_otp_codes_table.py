"""create_otp_codes_table

Revision ID: 3634d43f5c5a
Revises: 07d7e8739bbf
Create Date: 2025-11-30 12:41:28.329130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3634d43f5c5a'
down_revision: Union[str, None] = '07d7e8739bbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'otp_codes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('type', sa.String(), nullable=False, index=True),
        sa.Column('hashed_code', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    # Composite index for efficient latest code lookup
    op.create_index('idx_otp_user_type_created', 'otp_codes', ['user_id', 'type', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_otp_user_type_created', table_name='otp_codes')
    op.drop_index(op.f('ix_otp_codes_expires_at'), table_name='otp_codes')
    op.drop_index(op.f('ix_otp_codes_type'), table_name='otp_codes')
    op.drop_index(op.f('ix_otp_codes_user_id'), table_name='otp_codes')
    op.drop_table('otp_codes')

