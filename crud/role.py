from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.role import Role
from models.staff import Staff


class RoleCRUD:
    @staticmethod
    def get_roles(db: Session):
        roles = db.scalars(select(Role)).all()
        return roles

    @staticmethod
    def get_role_by_name(db: Session, name: str):
        role = db.scalar(select(Role).where(Role.name == name))
        return role

    @staticmethod
    def grant_role(db: Session, staff: Staff, role_name: str):
        role = RoleCRUD.get_role_by_name(db, role_name)
        if role is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Role not found")

        staff.role_id = role.id
        return staff


role_crud = RoleCRUD()
