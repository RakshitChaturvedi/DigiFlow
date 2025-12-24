from sqlalchemy import Column, BigInteger, String, JSON, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from app.db.base_class import Base


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)

    method = Column(String, nullable=False)
    path = Column(String, nullable=False)

    idempotency_key = Column(String, nullable=False)
    request_hash = Column(String, nullable=False)

    response_status = Column(BigInteger, nullable=False)
    response_body = Column(JSON, nullable=True)
    response_headers = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_idempotency_tenant_key"
        ),
    )
