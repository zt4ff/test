from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import get_current_active_user, require_permission
from crud.sales import sales_crud
from database.database import get_db
from models.staff import Staff
from models.user import User
from schemas.sales import SaleCreate, SaleOut

sales_router = APIRouter()


@sales_router.post(
    "/{store_id}/sales/", response_model=SaleOut, status_code=status.HTTP_201_CREATED
)
async def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("sales.create")),
):
    sale = sales_crud.create_sale(db, sale_data, created_by=current_staff.id)
    return sale


@sales_router.get("/{store_id}/sales/", response_model=List[SaleOut])
async def get_all_sales(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("sales.view")),
):
    return sales_crud.get_all_sales(db, store_id)


@sales_router.delete(
    "/{store_id}/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_sale(
    sale_id: UUID,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("sales.delete")),
):
    sales_crud.delete_sale(db, sale_id, current_staff.id)
    return


@sales_router.get("/{store_id}/sales/stats")
async def get_sales_stats(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("analytics.view")),
):
    return sales_crud.get_sales_stats(db, store_id)
