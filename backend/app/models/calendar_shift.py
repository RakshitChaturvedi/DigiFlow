from sqlalchemy import Column, BigInteger, String, Time, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class CalendarShift(Base):
    __tablename__ = "calendar_shifts"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    machine_id = Column(
        BigInteger, ForeignKey("machines.id", ondelete="SET NULL"), nullable=True
    )

    shift_name = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    days = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
    machine = relationship("Machine")
