from datetime import datetime, timezone
from typing import Optional, Tuple, List

from sqlalchemy import select, asc, desc, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineUpdate
from app.core.errors import DigiFlowException, ErrorCode


def create_machine(db: Session, tenant_id: int, data: MachineCreate) -> Machine:
    machine = Machine(
        tenant_id=tenant_id,
        name=data.name,
        external_id=data.external_id,
        meta=data.meta,
    )

    try:
        db.add(machine)
        db.commit()
        db.refresh(machine)
        return machine
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            code=ErrorCode.CONFLICT,
            message="Machine with same external_id already exists",
        )


def get_machine_by_id(db: Session, tenant_id: int, machine_id: int) -> Machine:
    stmt = select(Machine).where(
        and_(Machine.id == machine_id, Machine.tenant_id == tenant_id)
    )

    machine = db.execute(stmt).scalar_one_or_none()
    if not machine:
        raise DigiFlowException(ErrorCode.NOT_FOUND, "Machine not found")

    return machine


def list_machines(
    db: Session,
    tenant_id: int,
    cursor: Optional[int],
    limit: int,
    search: Optional[str],
    sort: str,
) -> Tuple[List[Machine], Optional[int]]:

    stmt = select(Machine).where(Machine.tenant_id == tenant_id)

    if search:
        stmt = stmt.where(Machine.name.ilike(f"%{search}%"))

    if sort == "name_asc":
        stmt = stmt.order_by(asc(Machine.name))
    elif sort == "name_desc":
        stmt = stmt.order_by(desc(Machine.name))
    else:
        stmt = stmt.order_by(asc(Machine.id))

    if cursor is not None:
        if sort.startswith("name"):
            raise DigiFlowException(
                ErrorCode.INVALID_INPUT,
                "Cursor pagination not supported with name sorting",
            )
        stmt = stmt.where(Machine.id > cursor)

    stmt = stmt.limit(limit + 1)
    rows = db.execute(stmt).scalars().all()

    next_cursor = rows[-1].id if len(rows) > limit else None
    return rows[:limit], next_cursor


def update_machine(
    db: Session,
    tenant_id: int,
    machine_id: int,
    data: MachineUpdate,
    if_unmodified_since: Optional[datetime],
) -> Machine:

    machine = get_machine_by_id(db, tenant_id, machine_id)

    if if_unmodified_since and machine.updated_at > if_unmodified_since:
        raise DigiFlowException(
            ErrorCode.CONFLICT, "Machine was modified by another request"
        )

    if data.name is not None:
        machine.name = data.name
    if data.external_id is not None:
        machine.external_id = data.external_id
    if data.meta is not None:
        machine.meta = data.meta

    machine.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(machine)
        return machine
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            code=ErrorCode.CONFLICT, message="Machine external_id already exists"
        )


def delete_machine(db: Session, tenant_id: int, machine_id: int) -> None:

    machine = get_machine_by_id(db, tenant_id, machine_id)

    db.delete(machine)
    db.commit()
