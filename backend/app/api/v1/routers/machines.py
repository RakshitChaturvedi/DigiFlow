from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Path, Header, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies.db import get_db
from app.schemas.machine import (
    MachineCreate,
    MachineResponse,
    MachineUpdate,
    MachineListResponse,
)
from app.services.machine_service import (
    create_machine,
    get_machine_by_id,
    list_machines,
    update_machine,
    delete_machine,
)
from app.schemas.current_user import CurrentUser
from app.api.v1.dependencies.get_current_user import get_current_user
from app.core.rbac import require_role
from app.core.errors import DigiFlowException, ErrorCode


router = APIRouter(prefix="/tenants/{tenant_id}/machines", tags=["machines"])


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
@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
@require_role("manager")
def create_machine_api(
    payload: MachineCreate,
    tenant_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return create_machine(db, tenant_id, payload)


# get single
@router.get("/{machine_id}", response_model=MachineResponse)
@require_role("operator")
def get_machine_api(
    tenant_id: int = Path(...),
    machine_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    return get_machine_by_id(db, tenant_id, machine_id)


# get list
@router.get("", response_model=MachineListResponse)
@require_role("operator")
def list_machines_api(
    tenant_id: int = Path(...),
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: str = Query("id_asc"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    items, next_cursor = list_machines(
        db=db, tenant_id=tenant_id, cursor=cursor, limit=limit, search=search, sort=sort
    )

    return {"data": items, "next_cursor": next_cursor}


# update
@router.patch("/{machine_id}", response_model=MachineResponse)
@require_role("manager")
def update_machine_api(
    payload: MachineUpdate,
    tenant_id: int = Path(...),
    machine_id: int = Path(...),
    if_unmodified_since: Optional[datetime] = Header(None, alias="If-Unmodified-Since"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    if not payload.model_dump(exclude_unset=True):
        raise DigiFlowException(
            code=ErrorCode.INVALID_INPUT, message="At least one field must be updated"
        )

    return update_machine(
        db=db,
        tenant_id=tenant_id,
        machine_id=machine_id,
        data=payload,
        if_unmodified_since=if_unmodified_since,
    )


# delete
@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role("manager")
def delete_machine_api(
    tenant_id: int = Path(...),
    machine_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(validate_tenant_access),
):
    delete_machine(db, tenant_id, machine_id)
    return None
