"""ddd: setup_matrix, calendar_shift, import_record, plugin_config

Revision ID: cef1688b299a
Revises: 5cfce4568cf0
Create Date: 2025-12-01 15:15:06.831906

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cef1688b299a"
down_revision: Union[str, Sequence[str], None] = "5cfce4568cf0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # SetupMatrix
    op.create_table(
        "setup_matrices",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("matrix", sa.JSON(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_setup_matrices_id", "setup_matrices", ["id"])
    op.create_index("ix_setup_matrices_tenant_id", "setup_matrices", ["tenant_id"])

    # CalendarShift
    op.create_table(
        "calendar_shifts",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("machine_id", sa.BigInteger(), nullable=True),
        sa.Column("shift_name", sa.String(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("days", sa.JSON(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_calendar_shifts_id", "calendar_shifts", ["id"])
    op.create_index("ix_calendar_shifts_tenant_id", "calendar_shifts", ["tenant_id"])

    # ImportRecord
    op.create_table(
        "import_records",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("importer_user_id", sa.BigInteger(), nullable=True),
        sa.Column("file_name", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["importer_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_import_records_id", "import_records", ["id"])
    op.create_index("ix_import_records_tenant_id", "import_records", ["tenant_id"])

    # PluginConfig
    op.create_table(
        "plugin_configs",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("plugin_name", sa.String(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plugin_configs_id", "plugin_configs", ["id"])
    op.create_index("ix_plugin_configs_tenant_id", "plugin_configs", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_plugin_configs_tenant_id", table_name="plugin_configs")
    op.drop_index("ix_plugin_configs_id", table_name="plugin_configs")
    op.drop_table("plugin_configs")

    op.drop_index("ix_import_records_tenant_id", table_name="import_records")
    op.drop_index("ix_import_records_id", table_name="import_records")
    op.drop_table("import_records")

    op.drop_index("ix_calendar_shifts_tenant_id", table_name="calendar_shifts")
    op.drop_index("ix_calendar_shifts_id", table_name="calendar_shifts")
    op.drop_table("calendar_shifts")

    op.drop_index("ix_setup_matrices_tenant_id", table_name="setup_matrices")
    op.drop_index("ix_setup_matrices_id", table_name="setup_matrices")
    op.drop_table("setup_matrices")
