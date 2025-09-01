from typing import Optional, Sequence
from uuid import UUID

from pydantic import BaseModel, EmailStr


class StoreCreate(BaseModel):
    name: str
    category: str
    no_of_staff: str


class StoreOut(StoreCreate):
    id: UUID
    user_id: UUID


class StoreInvite(BaseModel):
    store_id: Optional[UUID] = None
    staff_email: EmailStr
    role: str


class StoreInviteOut(BaseModel):
    status_code: int
    details: str


class StoreAcceptInvite(BaseModel):
    username: str
    password: str


class StoreInviteResend(BaseModel):
    store_id: Optional[UUID] = None
    staff_id: UUID


class StoreGenericResponseWithStoreData(BaseModel):
    status_code: int
    detail: str
    stores: Sequence[StoreOut]
