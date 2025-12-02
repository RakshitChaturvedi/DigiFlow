from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.core.security import verify_password
from app.core.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenDecodeError,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken


def login(db: Session, email: str, password: str, device_id: str):
    # authenticate user and create access + refresh tokens

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    if not verify_password(password, user.hashed_password):
        return None, "INVALID_PASSWORD"

    # create tokens
    access_token, access_jti, access_exp = create_access_token(
        user_id=user.id, tenant_id=user.tenant_id, role=user.role, device_id=device_id
    )

    refresh_token, refresh_jti, refresh_exp = create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        device_id=device_id,
        role=user.role,
    )

    # store refresh token in db
    try:
        db.add(
            RefreshToken(
                tenant_id=user.tenant_id,
                user_id=user.id,
                device_id=device_id,
                jti=refresh_jti,
                expires_at=refresh_exp,
                revoked=False,
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        return None, "INTEGRITY_ERROR"

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_expires_at": access_exp.isoformat(),
        "expires_in": int((access_exp - datetime.now(timezone.utc)).total_seconds()),
    }, None


def refresh(db: Session, refresh_token: str, device_id: str):
    # rotate refresh token, return new access + refresh token.
    # use "select .. for update" to avoid races. returns (result_dict, error_str)

    try:
        payload = decode_token(refresh_token)
    except TokenDecodeError as e:
        return None, str(e)

    if payload.get("type") != "refresh":
        return None, "INVALID_REFRESH_TOKEN"

    jti = payload.get("jti")
    if not jti:
        return None, "INVALID_REFRESH_TOKEN"

    now = datetime.now(timezone.utc)

    # lock refresh token raw to prevent concurrent refresh races.
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti)
        .with_for_update(of=RefreshToken)
        .first()
    )

    if not db_token:
        return None, "REFRESH_TOKEN_NOT_FOUND"

    if db_token.revoked:
        return None, "REFRESH_TOKEN_REVOKED"

    if db_token.device_id != device_id:
        return None, "DEVICE_MISMATCH"

    if db_token.expires_at < now:
        return None, "REFRESH_EXPIRED"

    # revoke old + insert new atomically
    try:
        db_token.revoked = True

        user_id = int(payload["sub"])
        tenant_id = payload["tenant_id"]

        # fetch curr role from db
        user = db.query(User).filter(User.id == user_id).one()
        role = user.role

        access_token, access_jti, access_exp = create_access_token(
            user_id=user_id, tenant_id=tenant_id, role=role, device_id=device_id
        )

        new_refresh_token, new_jti, new_exp = create_refresh_token(
            user_id=user_id, tenant_id=tenant_id, device_id=device_id
        )

        db.add(
            RefreshToken(
                tenant_id=tenant_id,
                user_id=user_id,
                device_id=device_id,
                jti=new_jti,
                expires_at=new_exp,
                revoked=False,
            )
        )

        db.commit()
    except IntegrityError:
        db.rollback()
        return None, "INTEGRITY_ERROR"
    except Exception:
        db.rollback()
        return None, "SERVER_ERROR"

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "access_expires_at": access_exp.isoformat(),
        "expires_in": int((access_exp - datetime.now(timezone.utc)).total_seconds()),
    }, None


def logout(db: Session, refresh_token: str):
    # Revoke refresh token, allow decoding expired tokens so logout possible even if refresh token expires.

    try:
        payload = decode_token(refresh_token, allow_expired=True)
    except TokenDecodeError:
        # if token cant be parsed, nothing to revoke
        return False

    jti = payload.get("jti")
    if not jti:
        return False

    db_token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if db_token and not db_token.revoked:
        db_token.revoked = True
        db.commit()

    return True
