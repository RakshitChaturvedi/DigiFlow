from pydantic import BaseModel, ConfigDict, StringConstraints, Field
from typing import Annotated, Optional, Dict, Any, List
from datetime import datetime


# base class
class RoutingBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str, StringConstraints(min_length=3, max_length=255, strip_whitespace=True)
    ]

    version: Annotated[int, Field(gt=0)]

    meta: Optional[Dict[str, Any]] = None


# "create" schema
class RoutingCreate(RoutingBase):
    product_id: int


# "update" schema
class RoutingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[
        Annotated[
            str, StringConstraints(min_length=3, max_length=255, strip_whitespace=True)
        ]
    ] = None

    version: Optional[Annotated[int, Field(gt=0)]] = None

    meta: Optional[Dict[str, Any]] = None


# "response" schema
class RoutingResponse(RoutingBase):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    tenant_id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    operations: List[Dict[str, Any]] = Field(default_factory=list)


# cursor pagination o/p envelope
class RoutingListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: List[RoutingResponse]
    next_cursor: Optional[str] = None
