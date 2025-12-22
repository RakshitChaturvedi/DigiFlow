from datetime import datetime, timezone
from typing import Optional, Tuple, List

from sqlalchemy import select, asc, desc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.routing import Routing
from app.models.product import Product
from app.schemas.routing import RoutingCreate, RoutingUpdate
from app.core.errors import DigiFlowException, ErrorCode


def create_routing(db: Session, tenant_id: int, data: RoutingCreate) -> Routing:

    product_exists = db.execute(
        select(Product.id).where(
            and_(Product.id == data.product_id, Product.tenant_id == tenant_id)
        )
    ).scalar_one_or_none()

    if not product_exists:
        raise DigiFlowException(code=ErrorCode.NOT_FOUND, message="Product not found")

    routing = Routing(
        tenant_id=tenant_id,
        product_id=data.product_id,
        name=data.name,
        version=data.version,
        meta=data.meta,
    )

    try:
        db.add(routing)
        db.commit()
        db.refresh(routing)
        return routing
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            ErrorCode.CONFLICT,
            "Routing version already exists for this product",
        )


def get_routing_by_id(db: Session, tenant_id: int, routing_id: int) -> Routing:
    stmt = select(Routing).where(
        and_(Routing.id == routing_id, Routing.tenant_id == tenant_id)
    )

    routing = db.execute(stmt).scalar_one_or_none()
    if not routing:
        raise DigiFlowException(ErrorCode.NOT_FOUND, "Routing not found")

    return routing


def list_routings(
    db: Session,
    tenant_id: int,
    product_id: Optional[int],
    cursor: Optional[int],
    limit: int,
    sort: str,
    search: Optional[str] = None,
) -> Tuple[List[Routing], Optional[int]]:

    stmt = select(Routing).where(Routing.tenant_id == tenant_id)

    if product_id:
        stmt = stmt.where(Routing.product_id == product_id)

    if search:
        stmt = stmt.where(Routing.name.ilike(f"%{search}%"))

    if sort == "name_asc":
        stmt = stmt.order_by(asc(Routing.name))
    elif sort == "name_desc":
        stmt = stmt.order_by(desc(Routing.name))
    elif sort == "version_desc":
        stmt = stmt.order_by(desc(Routing.version))
    else:
        stmt = stmt.order_by(asc(Routing.id))

    if cursor:
        if sort not in ["id_asc", ""]:
            raise DigiFlowException(
                ErrorCode.INVALID_INPUT,
                "Cursor pagination is only supported for default sorting (ID). Use offset for others.",
            )
        stmt = stmt.where(Routing.id > cursor)

    stmt = stmt.limit(limit + 1)
    rows = db.execute(stmt).scalars().all()

    next_cursor = rows[-1].id if len(rows) > limit else None
    return rows[:limit], next_cursor


def update_routing(
    db: Session,
    tenant_id: int,
    routing_id: int,
    data: RoutingUpdate,
    if_unmodified_since: Optional[datetime],
) -> Routing:
    routing = get_routing_by_id(db, tenant_id, routing_id)

    if if_unmodified_since and routing.updated_at > if_unmodified_since:
        raise DigiFlowException(
            ErrorCode.CONFLICT, "Routing was modified by another request"
        )

    if data.version is not None:
        routing.version = data.version
    if data.name is not None:
        routing.name = data.name
    if data.meta is not None:
        routing.meta = data.meta

    routing.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(routing)
        return routing
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            code=ErrorCode.CONFLICT, message="Routing name/version conflict"
        )


def delete_routing(db: Session, tenant_id: int, routing_id: int) -> None:
    routing = get_routing_by_id(db, tenant_id, routing_id)
    db.delete(routing)
    db.commit()
