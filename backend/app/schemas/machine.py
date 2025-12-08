from pydantic import BaseModel, ConfigDict, StringConstraints, Field
from typing import List, Optional, Any, Dict, Annotated
from datetime import datetime


# base class
class MachineBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str, StringConstraints(min_length=3, max_length=64, strip_whitespace=True)
    ]

    meta: Optional[Dict[str, Any]] = None


# "create" schema
class MachineCreate(MachineBase):
    model_config = ConfigDict(extra="forbid")

    external_id: Optional[
        Annotated[str, StringConstraints(max_length=64, strip_whitespace=True)]
    ] = None


# "update" schema
class MachineUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[
        Annotated[
            str, StringConstraints(min_length=3, max_length=64, strip_whitespace=True)
        ]
    ] = None

    external_id: Optional[
        Annotated[str, StringConstraints(max_length=64, strip_whitespace=True)]
    ] = None

    meta: Optional[Dict[str, Any]] = None


# "response" schema
class MachineResponse(MachineBase):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    tenant_id: int
    external_id: Optional[
        Annotated[str, StringConstraints(max_length=64, strip_whitespace=True)]
    ] = None

    # IMPORTANTTTTTTTTTTTTTTT!!!!
    # REFACTOR THESE WHEN MACHINE_CAPABILITY AND CALENDAR_SHIFTS SCHEMAS ARE CREATED
    capabilities: List[Dict[str, Any]] = Field(default_factory=list)
    calendar_shifts: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


# cursor pagination o/p envelope
class MachineListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: List[MachineResponse]
    next_cursor: Optional[str] = None
