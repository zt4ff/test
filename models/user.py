import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String)
    role = Column(String, default="Admin")
    is_active = Column(Boolean, default=True)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stores = relationship("Store", back_populates="owner")
    inventories = relationship("Inventory", back_populates="creator")
    sales_created = relationship(
        "Sale", back_populates="created_by_user", foreign_keys="Sale.created_by"
    )
    staff_profile = relationship("Staff", back_populates="user")
