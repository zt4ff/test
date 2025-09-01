from uuid import UUID

from fastapi import APIRouter, Depends, status,UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from config import get_current_active_user, require_permission
from crud.inventory import inventory_crud
from database.database import get_db
from models.staff import Staff
from models.user import User
from schemas.errors import ErrorOut
from schemas.inventory import (
    InventoryCreate,
    InventoryGenericResponseWithData,
    InventoryUpdate,
)
from schemas.utils import GenericResponse

inventory_router = APIRouter()


@inventory_router.post(
    "/{store_id}/inventory/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": InventoryGenericResponseWithData},
        400: {"model": ErrorOut},
    },
)
async def create_inventory(
    store_id: UUID,
    product_name: str = Form(...),
    cost_price: float = Form(...),
    selling_price: float = Form(...),
    sku: str = Form(...),
    quantity: int = Form(...),
    low_stock_threshold: int = Form(None),
    high_stock_threshold: int = Form(None),
    status_: str = Form("available"),
    expiration_date: str = Form(None),
    description: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("products.create")),
):
    inventory_data = InventoryCreate(
        product_name=product_name,
        cost_price=cost_price,
        selling_price=selling_price,
        sku=sku,
        quantity=quantity,
        low_stock_threshold=low_stock_threshold,
        high_stock_threshold=high_stock_threshold,
        status=status_,
        expiration_date=expiration_date,
        description=description,
    )
    new_inventory = await inventory_crud.create_inventory(
        db=db,
        inventory_data=inventory_data,
        created_by=current_staff.user.id,
        store_id=store_id,
        file=file,
    )
    return {
        "status_code": status.HTTP_201_CREATED,
        "detail": "Inventory item created successfully",
        "inventory": new_inventory,
    }


# TODO: remove function for data privacy
@inventory_router.get(
    "/inventory",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": InventoryGenericResponseWithData},
        404: {"model": ErrorOut},
    },
)
async def get_all_inventory(db: Session = Depends(get_db)):
    inventory_items = inventory_crud.get_inventory(db)
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "Inventory data retrieved",
        "inventory": inventory_items,
    }


@inventory_router.get(
    "/{store_id}/inventory",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": InventoryGenericResponseWithData},
        404: {"model": ErrorOut},
    },
)
async def get_inventory_by_store(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("products.view")),
):
    inventory_items =  inventory_crud.get_inventory_by_store_id(db, store_id)
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "store inventory retrieved",
        "inventory": inventory_items,
    }


@inventory_router.patch(
    "/{store_id}/inventory/{inventory_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": InventoryGenericResponseWithData},
        404: {"model": ErrorOut},
    },
)
async def update_inventory(
    inventory_id: UUID,
    product_name: str =Form(None),
    cost_price: float = Form(None),
    selling_price: float = Form(None),
    quantity: int = Form(None),
    status_: str =Form(None) ,
    description: str = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks,
    current_staff: Staff = Depends(require_permission("products.edit")),
):  
    
    inventory_data = InventoryUpdate(
        product_name=product_name,
        cost_price=cost_price,
        selling_price=selling_price,
        quantity=quantity,
        status=status_,
        description=description,
    )
    updated_inventory =  inventory_crud.update_inventory(
        db, inventory_id, inventory_data,
        file=file,
        background_tasks=background_tasks
    )
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "Inventory item updated successfully",
        "inventory": updated_inventory,
    }


@inventory_router.delete(
    "/{store_id}/inventory/{inventory_id}",
    status_code=status.HTTP_200_OK,
    responses={200: {"model": GenericResponse}, 404: {"model": ErrorOut}},
)
async def delete_inventory(
    inventory_id: UUID,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("products.delete")),
):
    inventory_crud.delete_inventory(db, inventory_id)
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "Inventory item deleted successfully",
    }
