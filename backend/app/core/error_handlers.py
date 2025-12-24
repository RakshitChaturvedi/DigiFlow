from typing import cast, Dict, Any

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


from app.core.errors import DigiFlowException, ErrorCode
from app.schemas.error_response import ErrorResponse, ErrorInfo, ErrorDetail


def register_error_handlers(app):

    @app.exception_handler(DigiFlowException)
    async def digiflow_exception_handler(request: Request, exc: DigiFlowException):

        if exc.code == ErrorCode.IDEMPOTENCY_REPLAY:
            cached_data = cast(Dict[str, Any], exc.details)

            return JSONResponse(
                status_code=cached_data["status"],
                content=cached_data["body"],
                headers=cached_data.get("headers") or {},
            )

        resp = ErrorResponse(
            error=ErrorInfo(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                request_id=getattr(request.state, "request_id", None),
            )
        )

        status_map = {
            ErrorCode.INVALID_INPUT: HTTP_400_BAD_REQUEST,
            ErrorCode.NOT_FOUND: HTTP_404_NOT_FOUND,
            ErrorCode.UNAUTHORIZED: HTTP_401_UNAUTHORIZED,
            ErrorCode.FORBIDDEN: HTTP_403_FORBIDDEN,
            ErrorCode.CONFLICT: HTTP_409_CONFLICT,
            ErrorCode.IDEMPOTENCY_REUSE_CONFLICT: HTTP_409_CONFLICT,
            ErrorCode.RATE_LIMIT_EXCEEDED: HTTP_429_TOO_MANY_REQUESTS,
            ErrorCode.JOB_FAILED: HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCode.SERVER_ERROR: HTTP_500_INTERNAL_SERVER_ERROR,
        }
        status_code = status_map.get(exc.code, 400)

        return JSONResponse(status_code=status_code, content=resp.model_dump())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # wrap fastapi's native errors into digiflow format
        resp = ErrorResponse(
            error=ErrorInfo(
                code=(
                    ErrorCode.UNAUTHORIZED
                    if exc.status_code == 401
                    else ErrorCode.INVALID_INPUT
                ),
                message=str(exc.detail),
                details=None,
                request_id=getattr(request.state, "request_id", None),
            )
        )
        return JSONResponse(status_code=exc.status_code, content=resp.model_dump())

    @app.exception_handler(Exception)
    async def fallback_handler(request: Request, exc: Exception):
        resp = ErrorResponse(
            error=ErrorInfo(
                code=ErrorCode.SERVER_ERROR,
                message="Internal server error.",
                details=[ErrorDetail(reason=str(exc))],
                request_id=getattr(request.state, "request_id", None),
            )
        )
        return JSONResponse(status_code=500, content=resp.model_dump())
