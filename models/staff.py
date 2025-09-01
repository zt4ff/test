import enum
import uuid

from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from database.database import Base


class StaffStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class Staff(Base):
    __tablename__ = "staffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"))
    status = Column(ENUM(StaffStatus), default=StaffStatus.PENDING, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)


    user = relationship("User", back_populates="staff_profile", viewonly=True)
    store = relationship("Store", back_populates="staffs", viewonly=True)
    role = relationship("Role", back_populates="staff", uselist=False)
    permission_overrides = relationship(
        "StaffPermissionOverride", back_populates="staff"
    )

    @property
    def role_name(self) -> str:
        return self.role.name if self.role else None
