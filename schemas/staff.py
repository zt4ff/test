from typing import Any, Optional, Sequence
from uuid import UUID

from pydantic import BaseModel

from models.staff import StaffStatus


class Staff(BaseModel):
    id: UUID
    user_id: UUID
    store_id: UUID
    status: StaffStatus
    role_id: Optional[UUID] = None
    role: Optional[str] = None


class StaffCreate(BaseModel):
    role: str
    user_id: UUID
    store_id: UUID
    role_id: Optional[UUID] = None


class StaffAdd(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[str] = None
    email: str
    role: str


class StaffUpdate(BaseModel):
    staff_id: UUID
    status: Optional[StaffStatus] = None
    role: Optional[str] = None


class StaffCreateOut(StaffCreate):
    id: UUID
    status: str


class StaffDetail(BaseModel):
    id: UUID
    user_id: UUID
    store_id: UUID
    status: StaffStatus
    role: str
    name: Optional[str] = None
    phone_no: Optional[str] = None
    email: Optional[str] = None
    login_time: Optional[str] = None
    logout_time: Optional[str] = None


class StaffGenericResponseWithAnyData(BaseModel):
    status_code: int
    detail: str
    data: Optional[Any] = None


class StaffGenericResponseWithStaffData(StaffGenericResponseWithAnyData):
    data: Optional[Staff] = None


class StaffsData(StaffGenericResponseWithAnyData):
    data: Optional[Sequence[StaffDetail]] = None


class StaffData(StaffGenericResponseWithAnyData):
    data: Optional[StaffDetail] = None
