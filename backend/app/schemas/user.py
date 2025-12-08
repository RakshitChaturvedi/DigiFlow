from pydantic import BaseModel, ConfigDict, StringConstraints, EmailStr
from typing import Annotated, Optional, Dict, Any, List
from datetime import datetime


# base class
class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[
        Annotated[
            str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)
        ]
    ] = None

    meta: Optional[Dict[str, Any]] = None


# "create" schema
class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr

    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]

    role: Annotated[
        str, StringConstraints(min_length=3, max_length=20, strip_whitespace=True)
    ]


# "update" schema
class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[
        Annotated[
            str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)
        ]
    ] = None

    meta: Optional[Dict[str, Any]] = None


# "response" schema
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    tenant_id: int
    email: EmailStr
    role: Annotated[
        str, StringConstraints(min_length=3, max_length=20, strip_whitespace=True)
    ]
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# cursor pagination o/p envelope
class UserListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: List[UserResponse]
    next_cursor: Optional[str] = None
