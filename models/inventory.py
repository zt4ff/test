from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    text,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base

stores_inventory: Table = Table(
    "stores_inventory",
    Base.metadata,
    Column("store_id", ForeignKey("stores.id"), primary_key=True),
    Column("inventory_id", ForeignKey("inventory.id"), primary_key=True),
)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_name = Column(String, nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)
    sku = Column(String, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    low_stock_threshold = Column(Integer)
    high_stock_threshold = Column(Integer)
    image_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="available")
    expiration_date = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )
    is_active = Column(Boolean, default=True, nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)

    @property
    def is_low_stock(self) -> bool:
        return self.current_stock <= self.low_stock_threshold

    @property
    def is_overstocked(self) -> bool:
        if self.high_stock_threshold is not None:
            return self.current_stock >= self.high_stock_threshold
        return False

    store = relationship(
        "Store", secondary=stores_inventory, back_populates="inventory"
    )
    creator = relationship("User", back_populates="inventories")
    sale_items = relationship("SaleItem", back_populates="inventory")
