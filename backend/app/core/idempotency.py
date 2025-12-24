import hashlib
import logging
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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
