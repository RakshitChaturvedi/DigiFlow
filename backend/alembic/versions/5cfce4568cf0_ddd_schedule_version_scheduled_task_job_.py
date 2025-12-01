"""ddd: schedule_version, scheduled_task, job_log

Revision ID: 5cfce4568cf0
Revises: 24642f2b6e6b
Create Date: 2025-12-01 15:00:58.684643

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5cfce4568cf0"
down_revision: Union[str, Sequence[str], None] = "24642f2b6e6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Schedule Versions
    op.create_table(
        "schedule_versions",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("generator_params", sa.JSON(), nullable=True),
        sa.Column("solver_meta", sa.JSON(), nullable=True),
        sa.Column("objective_score", sa.Numeric(), nullable=True),
        sa.Column("accepted_by_user", sa.BigInteger(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["accepted_by_user"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schedule_versions_id", "schedule_versions", ["id"])
    op.create_index(
        "ix_schedule_versions_tenant_id", "schedule_versions", ["tenant_id"]
    )

    # Scheduled Tasks
    op.create_table(
        "scheduled_tasks",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("schedule_version_id", sa.BigInteger(), nullable=False),
        sa.Column("operation_instance_id", sa.BigInteger(), nullable=False),
        sa.Column("machine_id", sa.BigInteger(), nullable=True),
        sa.Column("assigned_operator_id", sa.BigInteger(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["schedule_version_id"], ["schedule_versions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["operation_instance_id"], ["operation_instances.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["assigned_operator_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scheduled_tasks_id", "scheduled_tasks", ["id"])
    op.create_index("ix_scheduled_tasks_tenant_id", "scheduled_tasks", ["tenant_id"])

    # Job Logs
    op.create_table(
        "job_logs",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("task_id", sa.BigInteger(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["task_id"], ["scheduled_tasks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_logs_id", "job_logs", ["id"])
    op.create_index("ix_job_logs_tenant_id", "job_logs", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_job_logs_tenant_id", table_name="job_logs")
    op.drop_index("ix_job_logs_id", table_name="job_logs")
    op.drop_table("job_logs")

    op.drop_index("ix_scheduled_tasks_tenant_id", table_name="scheduled_tasks")
    op.drop_index("ix_scheduled_tasks_id", table_name="scheduled_tasks")
    op.drop_table("scheduled_tasks")

    op.drop_index("ix_schedule_versions_tenant_id", table_name="schedule_versions")
    op.drop_index("ix_schedule_versions_id", table_name="schedule_versions")
    op.drop_table("schedule_versions")
