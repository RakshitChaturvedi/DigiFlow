import hashlib
import logging
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.current_user import CurrentUser
from app.core.errors import DigiFlowException, ErrorCode
from app.models.idempotency_record import IdempotencyRecord


logger = logging.getLogger(__name__)


def hash_request_body(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def check_idempotency(
    *,
    db: Session,
    tenant_id: int,
    user_id: int,
    method: str,
    path: str,
    idempotency_key: str,
    request_hash: str
) -> Optional[IdempotencyRecord]:

    record = (
        db.query(IdempotencyRecord)
        .filter(
            IdempotencyRecord.tenant_id == tenant_id,
            IdempotencyRecord.idempotency_key == idempotency_key,
        )
        .one_or_none()
    )

    if record is None:
        return None

    if record.request_hash != request_hash:
        raise DigiFlowException(
            code=ErrorCode.IDEMPOTENCY_REUSE_CONFLICT,
            message="Idempotency key reused with different payload",
        )

    return record


def save_idempotency_response(
    *,
    db: Session,
    tenant_id: int,
    user_id: int,
    method: str,
    path: str,
    idempotency_key: str,
    request_hash: str,
    status_code: int,
    response_body: Optional[Dict[str, Any]],
    response_headers: Optional[Dict[str, Any]] = None
) -> None:
    record = IdempotencyRecord(
        tenant_id=tenant_id,
        user_id=user_id,
        method=method,
        path=path,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        response_status=status_code,
        response_body=response_body,
        response_headers=response_headers,
    )

    try:
        db.add(record)
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            "Idempotency Race Condition: Failed to save record for key %s (Tenant %s). "
            "Another request likely finished execution at the exact same time.",
            idempotency_key,
            tenant_id,
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Critical DB Failure: Could not save idempotency record. Error: %s",
            str(e),
            exc_info=True,
        )


def commit_idempotency(
    *,
    db: Session,
    current_user: CurrentUser,
    idempotency_ctx: dict,
    response_data: Any,
    status_code: int = 200,
    response_model: Optional[Type[BaseModel]] = None
):
    if response_model:
        json_body = response_model.model_validate(response_data).model_dump(mode="json")
    else:
        json_body = jsonable_encoder(response_data)

    save_idempotency_response(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        method=idempotency_ctx["method"],
        path=idempotency_ctx["path"],
        idempotency_key=idempotency_ctx["idempotency_key"],
        request_hash=idempotency_ctx["request_hash"],
        status_code=status_code,
        response_body=json_body,
    )
