from sqlalchemy import Column, BigInteger, DateTime, JSON, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    schedule_version_id = Column(
        BigInteger,
        ForeignKey("schedule_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    operation_instance_id = Column(
        BigInteger,
        ForeignKey("operation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    machine_id = Column(
        BigInteger, ForeignKey("machines.id", ondelete="SET NULL"), nullable=True
    )
    assigned_operator_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    scheduled_start_time = Column(DateTime(timezone=True), nullable=True)
    scheduled_end_time = Column(DateTime(timezone=True), nullable=True)

    status = Column(String, nullable=False)
    meta = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tenant = relationship("Tenant")
    schedule_version = relationship("ScheduleVersion")
    operation_instance = relationship("OperationInstance")
    machine = relationship("Machine")
    assigned_operator = relationship("User")
