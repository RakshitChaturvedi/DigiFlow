from sqlalchemy import Column, BigInteger, String, JSON, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)
    timezone = Column(String, nullable=False, server_default="UTC")
    currency = Column(String, nullable=True)
    config = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
