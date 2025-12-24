from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Path, Header, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies.db import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.services.product_service import (
    create_product,
    get_product_by_id,
    list_products,
    update_product,
    delete_product,
)
from app.schemas.current_user import CurrentUser
from app.api.v1.dependencies.get_current_user import get_current_user
from app.core.rbac import require_role
from app.core.errors import DigiFlowException, ErrorCode


router = APIRouter(prefix="/tenants/{tenant_id}/products", tags=["products"])


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
@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@require_role("manager")
def create_product_api(
    payload: ProductCreate,
    tenant_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return create_product(db, tenant_id, payload)


# get single
@router.get("/{product_id}", response_model=ProductResponse)
@require_role("operator")
def get_product_api(
    tenant_id: int = Path(...),
    product_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return get_product_by_id(db, tenant_id, product_id)


# get list
@router.get("", response_model=ProductListResponse)
@require_role("operator")
def list_products_api(
    tenant_id: int = Path(...),
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: str = Query("id_asc"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    items, next_cursor = list_products(
        db=db, tenant_id=tenant_id, cursor=cursor, limit=limit, search=search, sort=sort
    )

    return {"data": items, "next_cursor": next_cursor}


# update
@router.patch("/{product_id}", response_model=ProductResponse)
@require_role("manager")
def update_product_api(
    payload: ProductUpdate,
    tenant_id: int = Path(...),
    product_id: int = Path(...),
    if_unmodified_since: Optional[datetime] = Header(None, alias="If-Unmodified-Since"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    if not payload.model_dump(exclude_unset=True):
        raise DigiFlowException(
            code=ErrorCode.INVALID_INPUT, message="At least one field must be updated"
        )

    return update_product(
        db=db,
        tenant_id=tenant_id,
        product_id=product_id,
        data=payload,
        if_unmodified_since=if_unmodified_since,
    )


# delete
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role("manager")
def delete_product_api(
    tenant_id: int = Path(...),
    product_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):

    delete_product(db, tenant_id, product_id)
    return None
