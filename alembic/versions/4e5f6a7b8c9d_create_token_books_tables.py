"""Create token_identities, token_book_issues, token_book_payments tables

Revision ID: 4e5f6a7b8c9d
Revises: 3f8a1b2c4d5e
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = '4e5f6a7b8c9d'
down_revision = '3f8a1b2c4d5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'token_identities',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('milk_type_id', sa.Integer(), sa.ForeignKey('milk_types.id'), nullable=False),
        sa.Column('token_number', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.UniqueConstraint('customer_id', 'milk_type_id', 'token_number', name='uq_token_identity_customer_milk_type_number'),
    )

    op.create_table(
        'token_book_issues',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('token_identity_id', sa.Integer(), sa.ForeignKey('token_identities.id'), nullable=False),
        sa.Column('issue_number', sa.Integer(), nullable=False),
        sa.Column('issue_date', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_sheet', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('status', sa.String(20), server_default='WAITING', nullable=False),
        sa.Column('remarks', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
    )

    op.create_table(
        'token_book_payments',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('token_book_issue_id', sa.Integer(), sa.ForeignKey('token_book_issues.id'), nullable=False),
        sa.Column('payment_mode', sa.String(20), nullable=False),
        sa.Column('payment_status', sa.String(20), server_default='PENDING', nullable=False),
        sa.Column('book_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('amount_paid', sa.Numeric(10, 2), server_default=sa.text('0'), nullable=False),
        sa.Column('balance_amount', sa.Numeric(10, 2), server_default=sa.text('0'), nullable=False),
        sa.Column('payment_date', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('collected_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('remarks', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table('token_book_payments')
    op.drop_table('token_book_issues')
    op.drop_table('token_identities')
