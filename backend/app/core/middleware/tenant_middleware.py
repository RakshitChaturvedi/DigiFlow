from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Optional

from app.core.tenant_context import current_tenant
from app.schemas.current_user import CurrentUser


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Store tenant_id in ContextVar so SQLAlchemy engine events can inject it into db connections.
    """

    async def dispatch(self, request: Request, call_next):
        user: Optional[CurrentUser] = getattr(request.state, "current_user", None)

        if user:
            # set tenant_id for this req scope
            token = current_tenant.set(user.tenant_id)
        else:
            # no tenant leaks from prev req
            token = current_tenant.set(None)

        try:
            response = await call_next(request)
        finally:
            # restore prev context
            current_tenant.reset(token)

        return response
