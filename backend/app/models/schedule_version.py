from sqlalchemy import Column, BigInteger, DateTime, JSON, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ScheduleVersion(Base):
    __tablename__ = "schedule_versions"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generated_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    generator_params = Column(JSON, nullable=True)
    solver_meta = Column(JSON, nullable=True)
    objective_score = Column(Numeric, nullable=True)
    accepted_by_user = Column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    meta = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
    user = relationship("User", foreign_keys=[accepted_by_user])
