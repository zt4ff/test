from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.staff import StaffStatus
from models.store import Store
from models.user import User
from schemas.staff import StaffCreate
from schemas.store import StoreCreate, StoreOut

from .role import role_crud
from .staff import staff_crud


class StoreCRUD:
    @staticmethod
    def create_store(db: Session, user: User, store_data: StoreCreate) -> Store:
        existing_user = db.scalar(select(User).where(User.id == user.id))
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user id does not exist"
            )

        existing_store = db.scalar(select(Store).where(Store.name == store_data.name))
        if existing_store:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="store name already exists"
            )

        new_store = Store(
            name=store_data.name,
            category=store_data.category,
            no_of_staffs=store_data.no_of_staff,
            user_id=user.id,
        )

        user = role_crud.grant_role(db, user, "Admin")

        db.add(new_store)
        db.commit()
        db.refresh(new_store)

        staff_crud.create_staff(
            db,
            StaffCreate(role="Admin", user_id=user.id, store_id=new_store.id),
            StaffStatus.ACTIVE,
        )

        return new_store

    @staticmethod
    def get_store_by_owner(db: Session, owner_id: UUID) -> Sequence[StoreOut]:
        stores = db.scalars(select(Store).where(Store.user_id == owner_id)).all()
        return stores

    @staticmethod
    def get_store_by_id(db: Session, store_id: UUID) -> StoreOut:
        store = db.scalar(select(Store).where(Store.id == store_id))

        if store is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="store not found"
            )
        return store

    @staticmethod
    def get_all_store(db:Session):
        return db.query(Store).all()
store_crud = StoreCRUD()
