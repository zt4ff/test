from fastapi import HTTPException, status, BackgroundTasks, UploadFile, File
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional
from schemas.inventory import InventoryCreate, InventoryUpdate
from models.inventory import Inventory
from services.mail import email_service
from models.store import Store
from models.staff import Staff
from models.user import User
from services.image_config import image_service


class InventoryCRUD:
    @staticmethod
    async def create_inventory(
        db: Session, inventory_data: InventoryCreate, created_by: UUID, store_id: UUID,
        file: UploadFile = File(None),
    ):
        existing = (
            db.query(Inventory).filter(Inventory.sku == inventory_data.sku).first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")
        store = (
            db.query(Store).filter(Store.id == store_id).first()
        )
        if not store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Valid Store ID is required"
            )
        # if not store.is_active:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST, detail="Store is not active"
        #     )
      
        image_url = None
        if file:
            image_url = await image_service.validate_and_upload_profile_picture(file,str(created_by))
        new_inventory = Inventory(
            product_name=inventory_data.product_name,
            cost_price=inventory_data.cost_price,
            selling_price=inventory_data.selling_price,
            sku=inventory_data.sku,
            low_stock_threshold=inventory_data.low_stock_threshold,
            high_stock_threshold=inventory_data.high_stock_threshold,
            quantity=inventory_data.quantity,
            status=inventory_data.status,
            description=inventory_data.description,
            expiration_date=inventory_data.expiration_date,
            created_by=created_by,
            store_id=store_id,
            image_url=image_url,
            is_active=True,
        )
        db.add(new_inventory)
        db.commit()
        db.refresh(new_inventory)
        return new_inventory

    @staticmethod
    def get_inventory(db: Session):
        return db.query(Inventory).filter(Inventory.is_active == True).all()

    # get inventory by store id
    @staticmethod
    def get_inventory_by_store_id(db: Session, store_id: UUID):
        inventory = (
            db.query(Inventory)
            .filter(Inventory.store_id == store_id, Inventory.is_active == True)
            .all()
        )
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No inventory found for this store",
            )
        return inventory

    @staticmethod
    def get_inventory_by_id(db: Session, inventory_id: UUID):
        inventory = (
            db.query(Inventory)
            .filter(Inventory.id == inventory_id, Inventory.is_active == True)
            .first()
        )
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found"
            )
        return inventory

    @staticmethod
    async def update_inventory(
        db: Session,
        inventory_id: UUID,
        inventory_data: InventoryUpdate,
        file: Optional [UploadFile] = File(None),
        background_tasks: BackgroundTasks = None,
    ):
        inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found"
            )
        # check if inventory item is active
        if not inventory.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inventory item is not active"
            )
        if file and file.filename:
            image_url = await image_service.validate_and_upload_profile_picture(file, str(inventory.created_by))
            inventory.image_url = image_url 
        for key, value in inventory_data.dict(exclude_unset=True).items():
            if value is not None:
              setattr(inventory, key, value)

        db.commit()
        db.refresh(inventory)
        # Low stock notification logic
        if inventory.quantity is not None and inventory.low_stock_threshold is not None:
            if inventory.quantity <= inventory.low_stock_threshold:
                # Get store and staff emails
                store = db.query(Store).filter(Store.id == inventory.store_id).first()
                staff_users = (
                    db.query(User)
                    .join(Staff, Staff.user_id == User.id)
                    .filter(Staff.store_id == store.id)
                    .all()
                )
                owner = db.query(User).filter(User.id == store.user_id).first()
                emails = [user.email for user in staff_users]
                if owner and owner.email not in emails:
                    emails.append(owner.email)
                # Send emails in background
                if background_tasks:
                    for email in emails:
                        background_tasks.add_task(
                            email_service.send_email,
                            email=email,
                            subject=f"Low Stock Alert: {inventory.product_name}",
                            body=f"The inventory for {inventory.product_name} is low (current: {inventory.quantity}). Please restock soon.",
                        )
        return inventory

    @staticmethod
    def delete_inventory(db: Session, inventory_id: UUID):
        inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found"
            )
        inventory.is_active = False

        db.commit()
        db.refresh(inventory)
        return {"detail": "Inventory item deleted successfully"}


inventory_crud = InventoryCRUD()
