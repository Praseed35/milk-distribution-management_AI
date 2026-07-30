"""merge token_books and delivery heads

Revision ID: aeecd8f99d6d
Revises: 4e5f6a7b8c9d, 5a6b7c8d9e0f
Create Date: 2026-07-29 19:26:56.266215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aeecd8f99d6d'
down_revision: Union[str, Sequence[str], None] = ('4e5f6a7b8c9d', '5a6b7c8d9e0f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
