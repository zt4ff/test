from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import (
    get_current_active_user,
    get_current_staff,
    require_any_permission,
    require_permission,
)
from database.database import get_db
from models.staff import Staff
from schemas.errors import ErrorOut
from schemas.utils import GenericResponseWithSequenceData
from services.permission import permission_service

permission_router = APIRouter()


@permission_router.get("/{store_id}/permission/{staff_id}", responses={400: {"model": ErrorOut}, 200: {"model": GenericResponseWithSequenceData}})
async def get_staff_permissions(
    staff_id: UUID,
    db: Session = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    permissions = permission_service.get_staff_permissions(db, staff_id)
    return GenericResponseWithSequenceData(status_code=status.HTTP_200_OK, detail="permissions retrieved", data=permissions)
