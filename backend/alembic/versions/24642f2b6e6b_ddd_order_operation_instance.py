"""ddd: order, operation_instance

Revision ID: 24642f2b6e6b
Revises: f8a2e5992e35
Create Date: 2025-12-01 14:35:49.442360

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "24642f2b6e6b"
down_revision: Union[str, Sequence[str], None] = "f8a2e5992e35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Orders table
    op.create_table(
        "orders",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("qty", sa.BigInteger(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_id", "orders", ["id"])
    op.create_index("ix_orders_tenant_id", "orders", ["tenant_id"])
    op.create_check_constraint("ck_orders_qty_positive", "orders", "qty > 0")

    # OperationInstances table
    op.create_table(
        "operation_instances",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("operation_id", sa.BigInteger(), nullable=False),
        sa.Column("qty", sa.BigInteger(), nullable=False),
        sa.Column("remaining_qty", sa.BigInteger(), nullable=True),
        sa.Column("estimated_time_s", sa.Integer(), nullable=True),
        sa.Column("dependencies", sa.JSON(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["operation_id"], ["operations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operation_instances_id", "operation_instances", ["id"])
    op.create_index(
        "ix_operation_instances_tenant_id", "operation_instances", ["tenant_id"]
    )
    op.create_check_constraint(
        "ck_operation_instances_qty_positive", "operation_instances", "qty > 0"
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_operation_instances_qty_positive", "operation_instances", type_="check"
    )
    op.drop_index("ix_operation_instances_tenant_id", table_name="operation_instances")
    op.drop_index("ix_operation_instances_id", table_name="operation_instances")
    op.drop_table("operation_instances")

    op.drop_constraint("ck_orders_qty_positive", "orders", type_="check")
    op.drop_index("ix_orders_tenant_id", table_name="orders")
    op.drop_index("ix_orders_id", table_name="orders")
    op.drop_table("orders")
