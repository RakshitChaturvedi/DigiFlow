from pydantic import BaseModel
from typing import Any, Optional, List

from app.core.errors import ErrorCode


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    reason: Optional[str] = None
    example: Optional[str] = None
    additional: Optional[Any] = None


class ErrorInfo(BaseModel):
    code: ErrorCode
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorInfo
