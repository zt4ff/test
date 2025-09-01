import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base

from .inventory import stores_inventory


class Store(Base):
    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256), nullable=False, unique=True)
    category = Column(String(256))
    no_of_staffs = Column(String(50), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    

    #Relationships
    owner = relationship("User", back_populates="stores")
    inventory = relationship(
        "Inventory", secondary=stores_inventory, back_populates="store")
    staffs = relationship("Staff", uselist=True, back_populates="store", viewonly=True)
    sales = relationship("Sale", back_populates="store")
    