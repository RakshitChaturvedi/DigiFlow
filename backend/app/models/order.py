from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    JSON,
    DateTime,
    CheckConstraint,
    Integer,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

    external_id = Column(String, nullable=True)  # ERP id
    qty = Column(BigInteger, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Integer, nullable=True, server_default="0")
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
    product = relationship("Product")

    __table_args__ = (CheckConstraint("qty > 0", name="ck_orders_qty_positive"),)
