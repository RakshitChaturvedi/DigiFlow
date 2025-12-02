from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy import text
from typing import Optional

from app.db.session import SessionLocal
from app.schemas.current_user import CurrentUser


class TenantRLSMiddleware(BaseHTTPMiddleware):
    """
    Binds postgres rls tenant context for every request that has authenticated user.
    steps:
        1. check if request.state.current_user is set
        2. if yes -> run sql: set app.current_tenant = <tenant_id>
        3. continue processing
        4. reset tenant at end for safety
    """

    async def dispatch(self, request: Request, call_next):
        # must cooperate w JWT extractor
        current_user: Optional[CurrentUser] = getattr(
            request.state, "current_user", None
        )

        if current_user:
            # open short db session just to apply tenant_id setting
            db = SessionLocal()

            try:
                db.execute(
                    text("SET app.current_tenant = :tenant_id"),
                    {"tenant_id": current_user.tenant_id},
                )
                db.commit()
            finally:
                db.close()

        response = await call_next(request)

        return response
