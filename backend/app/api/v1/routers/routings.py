from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Path, Header, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies.db import get_db
from app.schemas.routing import (
    RoutingCreate,
    RoutingUpdate,
    RoutingResponse,
    RoutingListResponse,
)
from app.services.routing_service import (
    create_routing,
    get_routing_by_id,
    list_routings,
    update_routing,
    delete_routing,
)
from app.schemas.current_user import CurrentUser
from app.api.v1.dependencies.get_current_user import get_current_user
from app.core.rbac import require_role
from app.core.errors import DigiFlowException, ErrorCode


router = APIRouter(prefix="/tenants/{tenant_id}/routings", tags=["routings"])


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
@router.post("", response_model=RoutingResponse, status_code=status.HTTP_201_CREATED)
@require_role("manager")
def create_routings_api(
    payload: RoutingCreate,
    tenant_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return create_routing(db, tenant_id, payload)


# get single
@router.get("/{routing_id}", response_model=RoutingResponse)
@require_role("operator")
def get_routing_api(
    tenant_id: int = Path(...),
    routing_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return get_routing_by_id(db, tenant_id, routing_id)


# get list
@router.get("", response_model=RoutingListResponse)
@require_role("operator")
def list_routings_api(
    tenant_id: int = Path(...),
    product_id: Optional[int] = Query(None, description="Filter by Product ID"),
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: str = Query("id_asc"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    items, next_cursor = list_routings(
        db=db,
        tenant_id=tenant_id,
        product_id=product_id,
        cursor=cursor,
        limit=limit,
        search=search,
        sort=sort,
    )

    return {"data": items, "next_cursor": next_cursor}


# update
@router.patch("/{routing_id}", response_model=RoutingResponse)
@require_role("manager")
def update_routing_api(
    payload: RoutingUpdate,
    tenant_id: int = Path(...),
    routing_id: int = Path(...),
    if_unmodified_since: Optional[datetime] = Header(None, alias="If-Unmodified-Since"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    if not payload.model_dump(exclude_unset=True):
        raise DigiFlowException(
            code=ErrorCode.INVALID_INPUT, message="At least one field must be updated"
        )

    return update_routing(
        db=db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        data=payload,
        if_unmodified_since=if_unmodified_since,
    )


# delete
@router.delete("/{routing_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role("manager")
def delete_routing_api(
    tenant_id: int = Path(...),
    routing_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    delete_routing(db, tenant_id, routing_id)
    return None
