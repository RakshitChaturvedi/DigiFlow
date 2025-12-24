"""add idempotency_records table

Revision ID: 10474eb6f493
Revises: 2588735dca19
Create Date: 2025-12-24 15:03:32.278596

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "10474eb6f493"
down_revision: Union[str, Sequence[str], None] = "2588735dca19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("request_hash", sa.String(), nullable=False),
        sa.Column("response_status", sa.BigInteger(), nullable=False),
        sa.Column("response_body", sa.JSON(), nullable=True),
        sa.Column("response_headers", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_idempotency_tenant_key",
        ),
    )

    op.create_index(
        "idx_idempotency_tenant_id",
        "idempotency_records",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_idempotency_tenant_id", table_name="idempotency_records")
    op.drop_table("idempotency_records")
