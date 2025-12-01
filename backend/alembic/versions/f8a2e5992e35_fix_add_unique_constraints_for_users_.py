"""fix: add unique constraints for users and products

Revision ID: f8a2e5992e35
Revises: 4d36eb95d2dd
Create Date: 2025-12-01 12:13:24.281341

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f8a2e5992e35"
down_revision: Union[str, Sequence[str], None] = "4d36eb95d2dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_unique_constraint(
        "uq_users_tenant_email", "users", ["tenant_id", "email"]
    )

    op.create_unique_constraint(
        "uq_products_tenant_sku", "products", ["tenant_id", "sku"]
    )


def downgrade():
    op.drop_constraint("uq_users_tenant_email", "users", type_="unique")

    op.drop_constraint("uq_products_tenant_sku", "products", type_="unique")
