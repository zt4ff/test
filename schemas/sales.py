from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class SaleItem(BaseModel):
    inventory_id: UUID
    quantity: int
    price: float  # price per unit at time of sale
    product_name: str


class SaleCreate(BaseModel):
    store_id: UUID
    items: List[SaleItem]
    payment_method: str
    amount_paid: float
    staff_id: UUID


class SaleOut(BaseModel):
    id: UUID
    store_id: UUID
    items: List[SaleItem]
    total_amount: float
    amount_paid: float
    change_given: float
    outstanding_balance: float
    payment_method: str
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
