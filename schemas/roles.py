from uuid import UUID
from typing import Optional, Sequence

from pydantic import BaseModel


class RoleSchema(BaseModel):
    id: UUID
    name: str
    description: str
    store_id: Optional[UUID] = None


class RolesGenericResponse(BaseModel):
    status_code: int
    detail: str


class RolesWithSequenceData(RolesGenericResponse):
    data: Optional[Sequence[RoleSchema]] = None
