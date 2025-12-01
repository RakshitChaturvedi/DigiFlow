from sqlalchemy import Column, BigInteger, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)
    meta = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
