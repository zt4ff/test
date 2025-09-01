from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.staff import Staff, StaffStatus
from models.store import Store
from models.user import User
from schemas.staff import StaffCreate

from .role import role_crud


class StaffCRUD:
    @staticmethod
    def create_staff(
        db: Session,
        staff_data: StaffCreate,
        staff_status: StaffStatus = StaffStatus.PENDING,
    ) -> Staff:
        existing_staff = db.scalar(
            select(Staff).where(
                Staff.user_id == staff_data.user_id,
                Staff.store_id == staff_data.store_id,
            )
        )

        if existing_staff:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="staff already exists"
            )

        existing_store = db.scalar(select(Store).where(Store.id == staff_data.store_id))
        if not existing_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="store not found"
            )

        new_staff = Staff(
            user_id=staff_data.user_id,
            store_id=staff_data.store_id,
            is_active=True,
            status=staff_status,
        )
        new_staff = role_crud.grant_role(db, new_staff, staff_data.role)

        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        return new_staff

    @staticmethod
    def get_staff_by_id(db: Session, staff_id: UUID) -> Staff:
        staff = db.scalar(select(Staff).where(Staff.id == staff_id))
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="staff not found"
            )
        return staff

    @staticmethod
    def get_staff_by_user_id(db: Session, store_id: UUID, user_id: UUID) -> Staff:
        staff = db.scalar(
            select(Staff).where(Staff.store_id == store_id, Staff.user_id == user_id)
        )
        return staff

    @staticmethod
    def get_all_store_staffs(db: Session, store_id: UUID) -> Sequence[Staff]:
        staff_list = db.scalars(select(Staff).where(Staff.store_id == store_id, Staff.is_active == True)).all()
        return staff_list


staff_crud = StaffCRUD()
