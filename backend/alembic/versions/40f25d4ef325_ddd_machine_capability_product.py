"""ddd: machine_capability, product

Revision ID: 40f25d4ef325
Revises: 5f3a7d6de2c4
Create Date: 2025-12-01 11:33:59.057729

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "40f25d4ef325"
down_revision: Union[str, Sequence[str], None] = "5f3a7d6de2c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "machine_capabilities",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_machine_capabilities_id", "machine_capabilities", ["id"])
    op.create_index(
        "ix_machine_capabilities_tenant_id", "machine_capabilities", ["tenant_id"]
    )

    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("sku", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_id", "products", ["id"])
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"])

    # ADD UNIQUE CONSTRAINT REQUIRED BY DDD
    op.create_unique_constraint(
        "uq_products_tenant_sku", "products", ["tenant_id", "sku"]
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint("uq_products_tenant_sku", "products", type_="unique")
    op.drop_index("ix_products_tenant_id", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")

    op.drop_index(
        "ix_machine_capabilities_tenant_id", table_name="machine_capabilities"
    )
    op.drop_index("ix_machine_capabilities_id", table_name="machine_capabilities")
    op.drop_table("machine_capabilities")
    # ### end Alembic commands ###
