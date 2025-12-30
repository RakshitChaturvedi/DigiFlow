from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Path, Header, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies.db import get_db
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderStatus,
)
from app.services.order_service import (
    create_order,
    get_order_by_id,
    list_orders,
    update_order,
    delete_order,
)
from app.schemas.current_user import CurrentUser
from app.api.v1.dependencies.get_current_user import get_current_user
from app.core.rbac import require_role
from app.core.errors import DigiFlowException, ErrorCode
from app.api.v1.dependencies.idempotency import require_idempotency
from app.core.idempotency import commit_idempotency


router = APIRouter(prefix="/tenants/{tenant_id}/orders", tags=["orders"])


def validate_tenant_access(
    tenant_id: int = Path(...), current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    if tenant_id != current_user.tenant_id:
        raise DigiFlowException(
            code=ErrorCode.FORBIDDEN,
            message="Tenant mismatch: You cannot access resources of another tenant",
        )

    return current_user


# create
@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
@require_role("manager")
def create_order_api(
    payload: OrderCreate,
    tenant_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
    idempotency_ctx: dict = Depends(require_idempotency),
):
    order = create_order(db, tenant_id, payload)

    commit_idempotency(
        db=db,
        current_user=current_user,
        idempotency_ctx=idempotency_ctx,
        response_data=order,
        status_code=status.HTTP_201_CREATED,
        response_model=OrderResponse,
    )

    return order


# get single
@router.get("/{order_id}", response_model=OrderResponse)
@require_role("operator")
def get_order_api(
    tenant_id: int = Path(...),
    order_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return get_order_by_id(db, tenant_id, order_id)


# get list
@router.get("", response_model=OrderListResponse)
@require_role("operator")
def list_orders_api(
    tenant_id: int = Path(...),
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None, description="Filter by Order Status"),
    sort: str = Query("id_asc"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    items, next_cursor = list_orders(
        db=db, tenant_id=tenant_id, cursor=cursor, limit=limit, status=status, sort=sort
    )

    return {"data": items, "next_cursor": next_cursor}


# update
@router.patch("/{order_id}", response_model=OrderResponse)
@require_role("manager")
def update_order_api(
    payload: OrderUpdate,
    tenant_id: int = Path(...),
    order_id: int = Path(...),
    if_unmodified_since: Optional[datetime] = Header(None, alias="If-Unmodified-Since"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
    idempotency_ctx: dict = Depends(require_idempotency),
):
    if not payload.model_dump(exclude_unset=True):
        raise DigiFlowException(
            code=ErrorCode.INVALID_INPUT, message="At least one field must be updated"
        )

    order = update_order(
        db=db,
        tenant_id=tenant_id,
        order_id=order_id,
        data=payload,
        if_unmodified_since=if_unmodified_since,
    )

    commit_idempotency(
        db=db,
        current_user=current_user,
        idempotency_ctx=idempotency_ctx,
        response_data=order,
        status_code=status.HTTP_200_OK,
        response_model=OrderResponse,
    )

    return order


# delete
@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role("manager")
def delete_order_api(
    tenant_id: int = Path(...),
    order_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):

    delete_order(db, tenant_id, order_id)
    return None
