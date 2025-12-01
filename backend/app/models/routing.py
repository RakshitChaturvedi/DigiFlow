from sqlalchemy import Column, BigInteger, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Routing(Base):
    __tablename__ = "routings"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String, nullable=True)
    version = Column(Integer, nullable=False, server_default="1")
    meta = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
    product = relationship("Product")
