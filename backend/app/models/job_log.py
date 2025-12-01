from sqlalchemy import Column, BigInteger, DateTime, JSON, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class JobLog(Base):
    __tablename__ = "job_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task_id = Column(
        BigInteger, ForeignKey("scheduled_tasks.id", ondelete="CASCADE"), nullable=False
    )
    event_type = Column(String, nullable=False)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    metadata_ = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
    task = relationship("ScheduledTask")
    user = relationship("User")
