from sqlalchemy import Column, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class SetupMatrix(Base):
    __tablename__ = "setup_matrices"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    matrix = Column(JSON, nullable=False)
    meta = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
