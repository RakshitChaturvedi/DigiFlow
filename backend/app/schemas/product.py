from typing import Annotated, Optional, Dict, Any, List
from pydantic import BaseModel, StringConstraints, ConfigDict
from datetime import datetime


# base schema
class ProductBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: Annotated[
        str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)
    ]

    name: Annotated[
        str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)
    ]

    meta: Optional[Dict[str, Any]] = None


# "create" schema
class ProductCreate(ProductBase):
    # fields required when creating a product
    pass


# "update" schema
class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[
        Annotated[
            str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)
        ]
    ] = None

    meta: Optional[Dict[str, Any]] = None


# "response" schema
class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime


# cursor pagination o/p envelope
class ProductListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: List[ProductResponse]
    next_cursor: Optional[str] = None
