"""add employee_code role route_id timestamps to employees

Revision ID: b3c4d5e6f7a8
Revises: 2a032b2352b4
Create Date: 2026-07-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = '2a032b2352b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add employee_code column
    op.add_column('employees', sa.Column(
        'employee_code', sa.String(20), nullable=True
    ))

    # Backfill existing employees with employee codes
    op.execute("""
        UPDATE employees
        SET employee_code = 'E' || LPAD(id::text, 5, '0')
    """)

    # Make employee_code NOT NULL and add unique constraint
    op.alter_column('employees', 'employee_code', nullable=False)
    op.create_unique_constraint(
        'uq_employees_employee_code',
        'employees', ['employee_code']
    )

    # Add role column
    op.add_column('employees', sa.Column(
        'role', sa.String(50), nullable=True
    ))

    # Backfill existing employees with default role
    op.execute("""
        UPDATE employees SET role = 'DELIVERY_PARTNER'
    """)

    # Make role NOT NULL
    op.alter_column('employees', 'role', nullable=False)

    # Add route_id FK
    op.add_column('employees', sa.Column(
        'route_id', sa.Integer(), nullable=True
    ))
    op.create_foreign_key(
        'fk_employees_route_id',
        'employees', 'routes',
        ['route_id'], ['id']
    )

    # Add phone unique constraint
    op.create_unique_constraint(
        'uq_employees_phone',
        'employees', ['phone']
    )

    # Add timestamps
    op.add_column('employees', sa.Column(
        'created_at',
        sa.DateTime(timezone=True),
        server_default=sa.text('now()')
    ))
    op.add_column('employees', sa.Column(
        'updated_at',
        sa.DateTime(timezone=True),
        server_default=sa.text('now()')
    ))

    # Add index on id
    op.create_index(
        op.f('ix_employees_id'),
        'employees', ['id'], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_employees_id'), table_name='employees')
    op.drop_column('employees', 'updated_at')
    op.drop_column('employees', 'created_at')
    op.drop_constraint('uq_employees_phone', 'employees', type_='unique')
    op.drop_constraint('fk_employees_route_id', 'employees', type_='foreignkey')
    op.drop_column('employees', 'route_id')
    op.drop_column('employees', 'role')
    op.drop_constraint('uq_employees_employee_code', 'employees', type_='unique')
    op.drop_column('employees', 'employee_code')
