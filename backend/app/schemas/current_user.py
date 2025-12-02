from pydantic import BaseModel


class CurrentUser(BaseModel):
    user_id: int
    tenant_id: int
    role: str
    device_id: str
    jti: str
