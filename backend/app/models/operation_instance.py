from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey,
    JSON,
    DateTime,
    Integer,
    CheckConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class OperationInstance(Base):
    __tablename__ = "operation_instances"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id = Column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    operation_id = Column(
        BigInteger, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False
    )

    qty = Column(BigInteger, nullable=False)
    remaining_qty = Column(BigInteger, nullable=True)
    estimated_time_s = Column(Integer, nullable=True)
    dependencies = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    update_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tenant = relationship("Tenant")
    order = relationship("Order")
    operation = relationship("Operation")

    __table_args__ = (
        CheckConstraint("qty>0", name="ck_operation_instances_qty_positive"),
    )
