import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.database import Base


class Sale(Base):
    __tablename__ = "sales"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(PG_UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    change_given = Column(Float, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    deleted_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    items = relationship("SaleItem", back_populates="sale")
    store = relationship("Store", back_populates="sales")
    created_by_user = relationship(
        "User", back_populates="sales_created", foreign_keys=[created_by]
    )


class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(PG_UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False)
    inventory_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=False
    )
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # price per unit at time of sale
    product_name = Column(String, nullable=False)

    sale = relationship("Sale", back_populates="items")
    inventory = relationship("Inventory", back_populates="sale_items")
