from datetime import datetime, timezone
from typing import Optional, Tuple, List

from sqlalchemy import select, asc, desc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import Product  # Needed for verification
from app.schemas.order import OrderCreate, OrderUpdate
from app.core.errors import DigiFlowException, ErrorCode


def create_order(db: Session, tenant_id: int, data: OrderCreate) -> Order:
    product_exists = db.execute(
        select(Product.id).where(
            and_(Product.id == data.product_id, Product.tenant_id == tenant_id)
        )
    ).scalar_one_or_none()

    if not product_exists:
        raise DigiFlowException(
            ErrorCode.NOT_FOUND, "Product not found or does not belong to this tenant"
        )

    # 2. Create Order
    order = Order(
        tenant_id=tenant_id,
        external_id=data.external_id,
        product_id=data.product_id,
        qty=data.qty,
        due_date=data.due_date,
        priority=data.priority,
        status="pending",
        meta=data.meta,
    )

    try:
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            ErrorCode.CONFLICT,
            "Order with this external_id already exists",
        )


def get_order_by_id(db: Session, tenant_id: int, order_id: int) -> Order:
    stmt = select(Order).where(and_(Order.id == order_id, Order.tenant_id == tenant_id))

    order = db.execute(stmt).scalar_one_or_none()
    if not order:
        raise DigiFlowException(ErrorCode.NOT_FOUND, "Order not found")

    return order


def list_orders(
    db: Session,
    tenant_id: int,
    cursor: Optional[int],
    limit: int,
    status: Optional[str],
    sort: str,
) -> Tuple[List[Order], Optional[int]]:
    stmt = select(Order).where(Order.tenant_id == tenant_id)

    if status:
        stmt = stmt.where(Order.status == status)

    if sort == "priority_desc":
        stmt = stmt.order_by(desc(Order.priority))
    elif sort == "due_date_asc":
        stmt = stmt.order_by(asc(Order.due_date))
    else:
        stmt = stmt.order_by(asc(Order.id))

    if cursor:
        if sort not in ["id_asc", "", None]:
            raise DigiFlowException(
                ErrorCode.INVALID_INPUT,
                "Cursor pagination is only supported for default sorting (ID). Use offset for others.",
            )
        stmt = stmt.where(Order.id > cursor)

    stmt = stmt.limit(limit + 1)
    rows = db.execute(stmt).scalars().all()

    next_cursor = rows[-1].id if len(rows) > limit else None
    return rows[:limit], next_cursor


def update_order(
    db: Session,
    tenant_id: int,
    order_id: int,
    data: OrderUpdate,
    if_unmodified_since: Optional[datetime],
) -> Order:
    order = get_order_by_id(db, tenant_id, order_id)

    if if_unmodified_since and order.updated_at > if_unmodified_since:
        raise DigiFlowException(
            ErrorCode.CONFLICT, "Order was modified by another request"
        )

    if data.qty is not None:
        order.qty = data.qty
    if data.due_date is not None:
        order.due_date = data.due_date
    if data.priority is not None:
        order.priority = data.priority
    if data.status is not None:
        order.status = data.status
    if data.external_id is not None:
        order.external_id = data.external_id
    if data.meta is not None:
        order.meta = data.meta

    order.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(order)
        return order
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(ErrorCode.CONFLICT, "Order external_id conflict")


def delete_order(db: Session, tenant_id: int, order_id: int) -> None:
    order = get_order_by_id(db, tenant_id, order_id)
    db.delete(order)
    db.commit()
