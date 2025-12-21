from datetime import datetime, timezone
from typing import Optional, Tuple, List

from sqlalchemy import select, asc, desc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)
from app.core.errors import DigiFlowException, ErrorCode


def create_product(db: Session, tenant_id: int, data: ProductCreate) -> Product:
    # create product, reject duplicates alr handled at db

    new_product = Product(
        tenant_id=tenant_id, sku=data.sku, name=data.name, meta=data.meta
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            code=ErrorCode.CONFLICT, message="Product SKU already exists"
        )


def get_product_by_id(db: Session, tenant_id: int, product_id: int) -> Product:

    stmt = select(Product).where(
        and_(Product.id == product_id, Product.tenant_id == tenant_id)
    )

    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise DigiFlowException(code=ErrorCode.NOT_FOUND, message="Product not found")

    return result


def list_products(
    db: Session,
    tenant_id: int,
    cursor: Optional[int],
    limit: int,
    search: Optional[str],
    sort: str,
) -> Tuple[List[Product], Optional[int]]:

    stmt = select(Product).where(Product.tenant_id == tenant_id)

    # filtering
    if search:
        stmt = stmt.where(Product.name.ilike(f"%{search}%"))

    # sorting
    if sort == "name_asc":
        stmt = stmt.order_by(asc(Product.name))
    elif sort == "name_desc":
        stmt = stmt.order_by(desc(Product.name))
    else:
        # default by id asc
        stmt = stmt.order_by(asc(Product.id))

    # cursor pagination
    if cursor is not None:
        if sort in ["name_asc", "name_desc"]:
            raise DigiFlowException(
                code=ErrorCode.INVALID_INPUT,
                message="Cursor pagination not supported for name sorting",
            )
        else:
            stmt = stmt.where(Product.id > cursor)

    stmt = stmt.limit(limit + 1)

    rows = db.execute(stmt).scalars().all()

    if len(rows) > limit:
        next_cursor = rows[-1].id
        rows = rows[:limit]
    else:
        next_cursor = None

    return rows, next_cursor


def update_product(
    db: Session,
    tenant_id: int,
    product_id: int,
    data: ProductUpdate,
    if_unmodified_since: Optional[datetime],
) -> Product:

    product = get_product_by_id(db, tenant_id, product_id)

    # optimistic concurrency check
    if if_unmodified_since and product.updated_at > if_unmodified_since:
        raise DigiFlowException(
            code=ErrorCode.CONFLICT, message="Resource was modified by another request"
        )

    # apply updates
    if data.name is not None:
        product.name = data.name

    if data.meta is not None:
        product.meta = data.meta

    product.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            code=ErrorCode.CONFLICT, message="Product update conflict"
        )


def delete_product(db: Session, tenant_id: int, product_id: int) -> None:

    product = get_product_by_id(db, tenant_id, product_id)

    db.delete(product)
    db.commit()
