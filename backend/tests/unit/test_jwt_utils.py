from datetime import datetime, timezone
import pytest

from app.core.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenDecodeError,
)
from app.core.config import settings


def test_create_acces_token_and_decode():
    token, jti, exp = create_access_token(
        user_id=1, tenant_id=100, role="manager", device_id="device_4732"
    )

    payload = decode_token(token)

    assert payload["sub"] == "1"
    assert payload["tenant_id"] == 100
    assert payload["role"] == "manager"
    assert payload["device_id"] == "device_4732"
    assert payload["jti"] == jti
    assert payload["type"] == "access"
    assert payload["iss"] == "digiflow_api"
    assert payload["aud"] == "digiflow_client"


def test_decode_invalid_token():
    with pytest.raises(TokenDecodeError):
        decode_token("random-ahh-string")


def test_refresh_token_includes_optinal_role():
    token, jti, exp = create_refresh_token(
        user_id=3, tenant_id=7, device_id="device_8932", role="operator"
    )

    payload = decode_token(token)

    assert payload["type"] == "refresh"
    assert payload["role"] == "operator"
    assert payload["tenant_id"] == 7


def test_expired_token_handling():
    expired_time = datetime.now(timezone.utc).replace(year=1973)

    token, jti, exp = create_access_token(
        user_id=1, tenant_id=1, role="manager", device_id="another-random-ahh-device"
    )

    from jose import jwt
    import uuid

    bad_payload = {
        "sub": "1",
        "tenant_id": 1,
        "role": "manager",
        "device_id": "another-random-ahh-device",
        "jti": str(uuid.uuid4()),
        "iss": "digiflow_api",
        "aud": "digiflow_client",
        "exp": expired_time,
        "type": "access",
    }

    expired_token = jwt.encode(bad_payload, settings.JWT_PRIVATE_KEY, algorithm="RS256")

    with pytest.raises(TokenDecodeError) as e:
        decode_token(expired_token)

    assert str(e.value) == "TOKEN_EXPIRED"
