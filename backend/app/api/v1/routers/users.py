from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Path, Header, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies.db import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.user_service import (
    create_user,
    get_user_by_id,
    list_users,
    update_user,
    delete_user,
)
from app.schemas.current_user import CurrentUser
from app.api.v1.dependencies.get_current_user import get_current_user
from app.core.rbac import require_role
from app.core.errors import DigiFlowException, ErrorCode
from app.api.v1.dependencies.idempotency import require_idempotency
from app.core.idempotency import commit_idempotency


router = APIRouter(prefix="/tenants/{tenant_id}/users", tags=["users"])


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
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@require_role("tenant_admin")
def create_user_api(
    payload: UserCreate,
    tenant_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
    idempotency_ctx: dict = Depends(require_idempotency),
):
    user = create_user(db, tenant_id, payload)

    commit_idempotency(
        db=db,
        current_user=current_user,
        idempotency_ctx=idempotency_ctx,
        response_data=user,
        status_code=status.HTTP_201_CREATED,
        response_model=UserResponse,
    )

    return user


# get single
@router.get("/{user_id}", response_model=UserResponse)
@require_role("tenant_admin")
def get_user_api(
    tenant_id: int = Path(...),
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return get_user_by_id(db, tenant_id, user_id)


# get list
@router.get("", response_model=UserListResponse)
@require_role("tenant_admin")
def list_users_api(
    tenant_id: int = Path(...),
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: str = Query("id_asc"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    items, next_cursor = list_users(
        db=db, tenant_id=tenant_id, cursor=cursor, limit=limit, search=search, sort=sort
    )

    return {"data": items, "next_cursor": next_cursor}


# update
@router.patch("/{user_id}", response_model=UserResponse)
@require_role("tenant_admin")
def update_user_api(
    payload: UserUpdate,
    tenant_id: int = Path(...),
    user_id: int = Path(...),
    if_unmodified_since: Optional[datetime] = Header(None, alias="If-Unmodified-Since"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
    idempotency_ctx: dict = Depends(require_idempotency),
):
    if not payload.model_dump(exclude_unset=True):
        raise DigiFlowException(
            code=ErrorCode.INVALID_INPUT, message="At least one field must be updated"
        )

    user = update_user(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        data=payload,
        if_unmodified_since=if_unmodified_since,
    )

    commit_idempotency(
        db=db,
        current_user=current_user,
        idempotency_ctx=idempotency_ctx,
        response_data=user,
        status_code=status.HTTP_200_OK,
        response_model=UserResponse,
    )

    return user


# delete
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role("tenant_admin")
def delete_user_api(
    tenant_id: int = Path(...),
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    delete_user(db, tenant_id, user_id)
    return None
