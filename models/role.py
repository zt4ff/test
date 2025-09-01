import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base

# Association table for many-to-many relationship
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", UUID, ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, index=True)
    description = Column(Text)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)

    # Relationships
    staff = relationship("Staff", back_populates="role")
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, index=True)  # e.g., "products.view"
    resource = Column(String(30))  # e.g., "products"
    action = Column(String(20))  # e.g., "view"

    # Relationships
    roles = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )


class StaffPermissionOverride(Base):
    __tablename__ = "staff_permission_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    staff_id = Column(UUID, ForeignKey("staffs.id"))
    permission_id = Column(UUID, ForeignKey("permissions.id"))
    granted = Column(Boolean)  # True = grant, False = deny
    reason = Column(Text)  # Optional reason for the override
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration

    # Relationships
    staff = relationship("Staff", back_populates="permission_overrides")
    permission = relationship("Permission")
