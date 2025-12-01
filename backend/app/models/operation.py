from sqlalchemy import Column, BigInteger, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Operation(Base):
    __tablename__ = "operations"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    routing_id = Column(
        BigInteger, ForeignKey("routings.id", ondelete="CASCADE"), nullable=False
    )

    seq_no = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    standard_time_s = Column(Integer, nullable=True)
    batch_size = Column(Integer, nullable=True)
    tool_requirements = Column(JSON, nullable=True)
    skill_requirements = Column(JSON, nullable=True)
    setup_group = Column(String, nullable=True)

    meta = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
    routing = relationship("Routing")
