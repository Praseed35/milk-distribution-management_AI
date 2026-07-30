"""Create delivery tables

Revision ID: 5a6b7c8d9e0f
Revises: 3f8a1b2c4d5e
Create Date: 2026-01-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

revision = '5a6b7c8d9e0f'
down_revision = '3f8a1b2c4d5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'delivery_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('route_id', sa.Integer(), sa.ForeignKey('routes.id'), nullable=False),
        sa.Column('delivery_date', sa.Date(), nullable=False),
        sa.Column('shift', sa.String(10), nullable=False),
        sa.Column('delivery_partner_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='PLANNED'),
        sa.Column('total_milk_loaded', sa.Numeric(10, 2), server_default='0'),
        sa.Column('total_token_registered', sa.Numeric(10, 2), server_default='0'),
        sa.Column('total_cash_sales', sa.Numeric(10, 2), server_default='0'),
        sa.Column('total_returned_milk', sa.Numeric(10, 2), server_default='0'),
        sa.Column('reconciliation_status', sa.String(20), server_default='PENDING'),
        sa.Column('reopened_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reopened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reopen_count', sa.Integer(), server_default='0'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.UniqueConstraint('route_id', 'delivery_date', 'shift', name='uq_session_route_date_shift'),
    )
    op.create_index('ix_delivery_sessions_status', 'delivery_sessions', ['status'])
    op.create_index('ix_delivery_sessions_delivery_date', 'delivery_sessions', ['delivery_date'])

    op.create_table(
        'daily_deliveries',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('delivery_sessions.id'), nullable=False),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('milk_type_id', sa.Integer(), sa.ForeignKey('milk_types.id'), nullable=False),
        sa.Column('planned_quantity', sa.Integer(), nullable=False),
        sa.Column('delivered_quantity', sa.Integer(), server_default='0'),
        sa.Column('delivery_status', sa.String(20), nullable=False),
        sa.Column('delivery_source', sa.String(20), nullable=False, server_default='PLANNED'),
        sa.Column('token_sheet_number', sa.Integer(), nullable=True),
        sa.Column('token_book_issue_id', sa.Integer(), sa.ForeignKey('token_book_issues.id'), nullable=True),
        sa.Column('added_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('added_reason', sa.String(500), nullable=True),
        sa.Column('cash_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_edited', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('last_edited_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('last_edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('shift', sa.String(10), nullable=False),
        sa.Column('delivery_date', sa.Date(), nullable=False),
        sa.Column('remarks', sa.String(500), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
    )
    op.create_index('ix_daily_deliveries_session_id', 'daily_deliveries', ['session_id'])
    op.create_index('ix_daily_deliveries_customer_id_delivery_date', 'daily_deliveries', ['customer_id', 'delivery_date'])
    op.create_index('ix_daily_deliveries_token_book_issue_id', 'daily_deliveries', ['token_book_issue_id'])
    op.create_index('ix_daily_deliveries_delivery_status', 'daily_deliveries', ['delivery_status'])

    op.create_table(
        'session_edits',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('delivery_sessions.id'), nullable=False),
        sa.Column('delivery_id', sa.Integer(), sa.ForeignKey('daily_deliveries.id'), nullable=True),
        sa.Column('edited_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('edit_type', sa.String(30), nullable=False),
        sa.Column('old_value', JSONB, nullable=False),
        sa.Column('new_value', JSONB, nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
    )
    op.create_index('ix_session_edits_session_id', 'session_edits', ['session_id'])
    op.create_index('ix_session_edits_delivery_id', 'session_edits', ['delivery_id'])
    op.create_index('ix_session_edits_edited_by', 'session_edits', ['edited_by'])

    op.create_table(
        'token_sheet_warnings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('delivery_id', sa.Integer(), sa.ForeignKey('daily_deliveries.id'), nullable=False),
        sa.Column('warning_code', sa.String(30), nullable=False),
        sa.Column('warning_message', sa.Text(), nullable=False),
        sa.Column('sheet_number', sa.Integer(), nullable=False),
        sa.Column('expected_sheet', sa.Integer(), nullable=True),
        sa.Column('book_issue_id', sa.Integer(), sa.ForeignKey('token_book_issues.id'), nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('acknowledged_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
    )
    op.create_index('ix_token_sheet_warnings_delivery_id', 'token_sheet_warnings', ['delivery_id'])
    op.create_index('ix_token_sheet_warnings_warning_code', 'token_sheet_warnings', ['warning_code'])


def downgrade() -> None:
    op.drop_table('token_sheet_warnings')
    op.drop_table('session_edits')
    op.drop_table('daily_deliveries')
    op.drop_table('delivery_sessions')
