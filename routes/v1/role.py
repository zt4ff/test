from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from config import (
    get_current_active_user,
    get_current_staff,
    require_any_permission,
    require_permission,
)
from database.database import get_db
from models.role import Role
from models.staff import Staff
from schemas.errors import ErrorOut
from schemas.roles import RolesWithSequenceData
from services.permission import permission_service

role_router = APIRouter()


@role_router.get(
    "/{store_id}/roles",
    responses={404: {"model": ErrorOut}, 200: {"model": RolesWithSequenceData}},
)
async def get_all_roles(
    store_id: UUID,
    db: Session = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    roles = db.scalars(
        select(Role).where(or_(Role.store_id == store_id, Role.store_id == None))
    ).all()
    return RolesWithSequenceData(
        status_code=status.HTTP_200_OK,
        detail="roles retrieved",
        data=jsonable_encoder(roles),
    )
