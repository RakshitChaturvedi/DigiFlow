from pydantic import BaseModel, ConfigDict, StringConstraints, Field
from typing import Annotated, Optional, Dict, Any, List
from datetime import date, datetime


# base class
class OrderBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priority: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None


# "create" schema
class OrderCreate(OrderBase):
    model_config = ConfigDict(extra="forbid")

    product_id: int

    quantity: Annotated[int, Field(gt=0)]

    due_date: date

    external_id: Optional[
        Annotated[
            str, StringConstraints(min_length=1, max_length=64, strip_whitespace=True)
        ]
    ] = None


# "update" class
class OrderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: Optional[Annotated[int, Field(gt=0)]] = None

    due_date: Optional[date] = None
    priority: Optional[int] = None

    external_id: Optional[
        Annotated[
            str, StringConstraints(min_length=1, max_length=64, strip_whitespace=True)
        ]
    ] = None

    meta: Optional[Dict[str, Any]] = None


# "response" schema
class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    tenant_id: int
    product_id: int
    due_date: date
    status: str

    external_id: Optional[
        Annotated[
            str, StringConstraints(min_length=1, max_length=64, strip_whitespace=True)
        ]
    ] = None

    created_at: datetime
    updated_at: datetime


# cursor pagination o/p envelope
class OrderListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: List[OrderResponse]
    next_cursor: Optional[str] = None
