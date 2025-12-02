from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request


from app.core.jwt_utils import decode_token, TokenDecodeError
from app.schemas.current_user import CurrentUser


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:

    # no authz header provided
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_HEADER_MISSING"
        )

    token = credentials.credentials

    # decode and validate jwt
    try:
        payload = decode_token(token)
    except TokenDecodeError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    # access-token-only
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="ACCESS_TOKEN_REQUIRED"
        )

    # extract fields (validated)
    try:
        user = CurrentUser(
            user_id=int(payload["sub"]),
            tenant_id=int(payload["tenant_id"]),
            role=str(payload["role"]),
            device_id=str(payload["device_id"]),
            jti=str(payload["jti"]),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="MALFORMED_TOKEN"
        )

    request.state.current_user = user
    request.state.current_tenant_id = user.tenant_id

    return user
