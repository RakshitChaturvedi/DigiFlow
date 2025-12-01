from sqlalchemy import Column, String, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class MachineCapability(Base):
    __tablename__ = "machine_capabilities"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    meta = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
