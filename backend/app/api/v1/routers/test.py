from fastapi import APIRouter, Depends, Request
from app.api.v1.dependencies.get_current_user import get_current_user
from app.schemas.current_user import CurrentUser
from app.core.rbac import require_role

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/admin-only")
@require_role("tenant_admin")
def admin_only(current_user: CurrentUser = Depends(get_current_user)):
    return {"ok": True, "user_role": current_user.role}


@router.get("/tenant-id")
def tenant_test(
    request: Request, current_user: CurrentUser = Depends(get_current_user)
):
    return {"tenant_id": request.state.current_tenant_id}
