"""fix: machine_capabilities tenant_id index

Revision ID: 4d36eb95d2dd
Revises: c96c0782e793
Create Date: 2025-12-01 12:09:47.393404

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4d36eb95d2dd"
down_revision: Union[str, Sequence[str], None] = "c96c0782e793"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index(
        "ix_machine_capabilities_tenant_id",
        "machine_capabilities",
        ["tenant_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_machine_capabilities_tenant_id", table_name="machine_capabilities"
    )
