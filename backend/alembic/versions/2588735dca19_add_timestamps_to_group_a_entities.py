"""add timestamps to group A entities

Revision ID: 2588735dca19
Revises: 90bc8b2887dd
Create Date: 2025-12-08 17:34:39.012816

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2588735dca19"
down_revision: Union[str, Sequence[str], None] = "90bc8b2887dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # PRODUCTS
    op.add_column(
        "products",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ROUTINGS
    op.add_column(
        "routings",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "routings",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ORDERS
    op.add_column(
        "orders",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("products", "created_at")
    op.drop_column("products", "updated_at")
    op.drop_column("routings", "created_at")
    op.drop_column("routings", "updated_at")
    op.drop_column("orders", "created_at")
    op.drop_column("orders", "updated_at")
