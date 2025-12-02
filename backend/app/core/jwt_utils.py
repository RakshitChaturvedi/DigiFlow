from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
import uuid

from app.core.config import settings


ALGORITHM = "RS256"
ISS = "digiflow_api"
AUD = "digiflow_client"


class TokenDecodeError(Exception):
    # raised when token cant be decoded/validated.
    pass


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _get_kid_header() -> Optional[Dict[str, str]]:
    # return a header dict with 'kid' if configured.
    kid = getattr(settings, "JWT_KEY_ID", None)
    if kid:
        return {"kid": kid}
    return None


def _select_public_key_for_kid(kid: Optional[str]) -> str:
    """
    choose public key to verift token based on kid
        if settings.JWT_PUBLIC_KEYS exists and contains kid, use it.
        else, fall back to settings.JWT_PUBLIC_KEY
    """

    public_keys = getattr(settings, "JWT_PUBLIC_KEYS", None)
    if kid and public_keys and kid in public_keys:
        return public_keys[kid]
    return settings.JWT_PUBLIC_KEY


def create_access_token(
    *, user_id: int, tenant_id: int, role: str, device_id: str
) -> Tuple[str, str, datetime]:

    expire = _now_utc() + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    jti = str(uuid.uuid4())

    payload = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "role": role,
        "device_id": device_id,
        "jti": jti,
        "iss": ISS,
        "aud": AUD,
        "exp": expire,
        "type": "access",
    }

    headers = _get_kid_header()
    token = jwt.encode(
        payload, settings.JWT_PRIVATE_KEY, algorithm=ALGORITHM, headers=headers
    )

    return token, jti, expire


def create_refresh_token(
    *,
    user_id: int,
    tenant_id: int,
    device_id: str,
    role: Optional[str] = None,
    days: int = 30
) -> Tuple[str, str, datetime]:
    # include role as optional convenience claim, prefer reading role from DB.

    expire = _now_utc() + timedelta(days=days)
    jti = str(uuid.uuid4())

    payload = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "device_id": device_id,
        "jti": jti,
        "iss": ISS,
        "aud": AUD,
        "exp": expire,
        "type": "refresh",
    }

    if role is not None:
        payload["role"] = role  # not authoritative.

    headers = _get_kid_header()
    token = jwt.encode(
        payload, settings.JWT_PRIVATE_KEY, algorithm=ALGORITHM, headers=headers
    )

    return token, jti, expire


def decode_token(token: str, allow_expired: bool = False) -> Dict:
    """
    Decode and validate token. raise TokenDecodeError on failure.

    allow_expired: if true, return payload even if token has expired
                    (useful for logout flows where revoking already-expired token)
    """

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
    except Exception:
        kid = None

    pubkey = _select_public_key_for_kid(kid)

    try:
        payload = jwt.decode(
            token,
            pubkey,
            algorithms=[ALGORITHM],
            audience=AUD,
            issuer=ISS,
        )
        return payload
    except ExpiredSignatureError:
        if allow_expired:
            try:
                payload = jwt.decode(
                    token,
                    pubkey,
                    algorithms=[ALGORITHM],
                    options={"verify_exp": False},
                )
                return payload
            except Exception:
                raise TokenDecodeError("INVALID_TOKEN")
        raise TokenDecodeError("TOKEN_EXPIRED")
    except JWTError:
        raise TokenDecodeError("INVALID_TOKEN")
