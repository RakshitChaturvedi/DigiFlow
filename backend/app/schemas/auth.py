from pydantic import BaseModel


class LoginIn(BaseModel):
    email: str
    password: str
    device_id: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    access_expires_at: str
    expires_in: int


class RefreshIn(BaseModel):
    refresh_token: str
    device_id: str


class LogoutIn(BaseModel):
    refresh_token: str
