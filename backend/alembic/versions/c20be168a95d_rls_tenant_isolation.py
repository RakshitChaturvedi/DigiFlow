"""rls: tenant isolation

Revision ID: c20be168a95d
Revises: cef1688b299a
Create Date: 2025-12-01 18:22:02.858558

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c20be168a95d"
down_revision: Union[str, Sequence[str], None] = "cef1688b299a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    tables = [
        "users",
        "machines",
        "machine_capabilities",
        "products",
        "routings",
        "operations",
        "orders",
        "operation_instances",
        "schedule_versions",
        "scheduled_tasks",
        "job_logs",
        "setup_matrices",
        "calendar_shifts",
        "import_records",
        "plugin_configs",
    ]

    for table in tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

        op.execute(
            f"""
            CREATE POLICY tenant_isolation_select ON {table}
                FOR SELECT USING (
                    tenant_id = current_setting('app.current_tenant')::bigint
                );
        """
        )

        op.execute(
            f"""
            CREATE POLICY tenant_isolation_modify ON {table}
                FOR ALL USING (
                    tenant_id = current_setting('app.current_tenant')::bigint
                ) WITH CHECK (
                    tenant_id = current_setting('app.current_tenant')::bigint
                );
        """
        )


def downgrade() -> None:
    """Downgrade schema."""
    tables = [
        "users",
        "machines",
        "machine_capabilities",
        "products",
        "routings",
        "operations",
        "orders",
        "operation_instances",
        "schedule_versions",
        "scheduled_tasks",
        "job_logs",
        "setup_matrices",
        "calendar_shifts",
        "import_records",
        "plugin_configs",
    ]

    for table in tables:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_select ON {table};")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_modify ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
