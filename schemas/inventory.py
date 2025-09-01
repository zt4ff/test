from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class InventoryItem(BaseModel):
    product_name: str
    cost_price: float
    selling_price: float
    sku: str
    low_stock_threshold: Optional[int] = None
    high_stock_threshold: Optional[int] = None
    quantity: int
    image_url: Optional[str] = None
    status: Optional[str] = "available"
    expiration_date: Optional[datetime] = None
    description: Optional[str] = None


class InventoryCreate(InventoryItem):
    pass


class InventoryOut(InventoryItem):
    id: UUID
    store_id: UUID
    is_active: bool = True
    image_url: Optional[str] = None
    created_by: UUID
    updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class InventoryUpdate(BaseModel):
    product_name: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    quantity: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    last_updated: datetime = datetime.utcnow()
    # last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    model_config = {"from_attributes": True}

class InventoryGenericResponseWithData(BaseModel):
    status_code: int
    detail: str
    inventory: Optional[InventoryOut] = None
