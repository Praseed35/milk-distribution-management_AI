"""add_report_indexes

Revision ID: 119aa199d5d7
Revises: 6a0f9777a5cb
Create Date: 2026-07-31 00:01:08.225766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '119aa199d5d7'
down_revision: Union[str, Sequence[str], None] = '6a0f9777a5cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_daily_deliveries_delivery_status", "daily_deliveries", ["delivery_status"])
    op.create_index("ix_customer_payments_payment_date", "customer_payments", ["payment_date"])
    op.create_index("ix_customer_bills_bill_period_start", "customer_bills", ["bill_period_start"])


def downgrade() -> None:
    op.drop_index("ix_daily_deliveries_delivery_status")
    op.drop_index("ix_customer_payments_payment_date")
    op.drop_index("ix_customer_bills_bill_period_start")
