from enum import Enum
from typing import Any, Optional


class ErrorCode(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    IDEMPOTENCY_REUSE_CONFLICT = "IDEMPOTENCY_REUSE_CONFLICT"
    IDEMPOTENCY_REPLAY = "IDEMPOTENCY_REPLAY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    JOB_FAILED = "JOB_FAILED"
    SERVER_ERROR = "SERVER_ERROR"


class DigiFlowException(Exception):
    # base structured exception, always produces strict envelope.
    def __init__(self, code: ErrorCode, message: str, details: Optional[Any] = None):
        self.code = code
        self.message = message
        self.details = details
