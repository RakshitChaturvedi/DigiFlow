from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.jwt_utils import decode_token, TokenDecodeError
from app.services.auth_service import login, refresh, logout
from app.schemas.auth import LoginIn, LogoutIn, TokenOut, RefreshIn

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=TokenOut)
def login_user(payload: LoginIn, db: Session = Depends(get_db)):
    result, error = login(db, payload.email, payload.password, payload.device_id)

    if error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=error)
    return result


@router.post("/refresh", response_model=TokenOut)
def refresh_token(payload: RefreshIn, db: Session = Depends(get_db)):
    result, error = refresh(db, payload.refresh_token, payload.device_id)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(payload: LogoutIn, db: Session = Depends(get_db)):
    logout(db, payload.refresh_token)
    return None


@router.get("/verify")
def verify_token(token: str):
    try:
        payload = decode_token(token)
    except TokenDecodeError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return payload
