import pytest
from fastapi import HTTPException

from app.core.rbac import has_privilege, require_role
from app.schemas.current_user import CurrentUser


def test_has_privileges():
    assert has_privilege("superadmin", "operator")
    assert has_privilege("manager", "operator")
    assert not has_privilege("operator", "manager")


def test_require_role_allows_authorized():
    @require_role("manager")
    def protected_route(current_user=None):
        return "ok"

    user = CurrentUser(
        user_id=1, tenant_id=1, role="manager", device_id="how-many-moreee", jti="j"
    )

    result = protected_route(current_user=user)
    assert result == "ok"


def test_require_role_rejects_unauthorized():
    @require_role("manager")
    def protected_route(current_user=None):
        return "ok"

    user = CurrentUser(
        user_id=1, tenant_id=1, role="operator", device_id="how-many-moreee", jti="j"
    )

    with pytest.raises(HTTPException) as e:
        protected_route(current_user=user)

    assert e.value.status_code == 403
