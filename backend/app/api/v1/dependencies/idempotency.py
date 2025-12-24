from fastapi import Request, Header, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies.db import get_db
from app.api.v1.dependencies.get_current_user import get_current_user
from app.schemas.current_user import CurrentUser
from app.core.errors import DigiFlowException, ErrorCode
from app.core.idempotency import check_idempotency, hash_request_body


async def require_idempotency(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # 1. read body (bytes) then put them back into request scope
    body_bytes = await request.body()

    # 2. hash
    request_hash = hash_request_body(body_bytes)

    # 3. check db
    record = check_idempotency(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        method=request.method,
        path=request.url.path,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )

    if record:
        # Dependencies cant easily stop execution and return a response.
        # Raise specific exception that global except handler catches and converts into replayed JSONresponse.

        raise DigiFlowException(
            code=ErrorCode.IDEMPOTENCY_REPLAY,
            message="Request replayed",
            details={
                "status": record.response_status,
                "body": record.response_body,
                "headers": record.response_headers,
            },
        )

    # 4. return context
    return {
        "idempotency_key": idempotency_key,
        "request_hash": request_hash,
        "method": request.method,
        "path": request.url.path,
    }
