"""add shift column to delivery_exceptions

Revision ID: a1b2c3d4e5f6
Revises: 119aa199d5d7
Create Date: 2026-07-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '119aa199d5d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'delivery_exceptions',
        sa.Column('shift', sa.String(10), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('delivery_exceptions', 'shift')
