from datetime import datetime
from typing import Dict, List, Union
from uuid import UUID

from sqlalchemy.orm import Session

from models.role import Permission, StaffPermissionOverride
from models.staff import Staff


class PermissionService:
    @staticmethod
    def get_staff_permissions(db: Session, staff_id: UUID) -> List[str]:
        """Get all effective permissions for a staff member (role + overrides)"""

        # Get base permissions from role
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            return []

        # Start with role permissions
        role_permissions = set()
        if staff.role:
            role_permissions = {perm.name for perm in staff.role.permissions}

        # Apply individual overrides
        final_permissions = PermissionService._apply_permission_overrides(
            db, staff_id, role_permissions
        )

        return list(final_permissions)

    @staticmethod
    def _apply_permission_overrides(
        db: Session, staff_id: UUID, base_permissions: set
    ) -> set:
        """Apply individual permission overrides to base permissions"""
        # Get all active overrides for this staff member
        overrides = (
            db.query(StaffPermissionOverride)
            .filter(
                StaffPermissionOverride.staff_id == staff_id,
                # Only include non-expired overrides
                (
                    StaffPermissionOverride.expires_at.is_(None)
                    | (StaffPermissionOverride.expires_at > datetime.utcnow())
                ),
            )
            .all()
        )

        final_permissions = base_permissions.copy()

        for override in overrides:
            permission_name = override.permission.name

            if override.granted:
                # Grant permission (add to set)
                final_permissions.add(permission_name)
            else:
                # Deny permission (remove from set)
                final_permissions.discard(permission_name)

        return final_permissions

    @staticmethod
    def get_staff_permission_details(db: Session, staff_id: UUID) -> Dict:
        """Get detailed breakdown of staff permissions including source"""
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            return {}

        # Get role permissions
        role_permissions = set()
        if staff.role:
            role_permissions = {perm.name for perm in staff.role.permissions}

        # Get overrides
        overrides = (
            db.query(StaffPermissionOverride)
            .filter(
                StaffPermissionOverride.staff_id == staff_id,
                (
                    StaffPermissionOverride.expires_at.is_(None)
                    | (StaffPermissionOverride.expires_at > datetime.utcnow())
                ),
            )
            .all()
        )

        override_grants = {o.permission.name for o in overrides if o.granted}
        override_denies = {o.permission.name for o in overrides if not o.granted}

        # Calculate final permissions
        final_permissions = (role_permissions | override_grants) - override_denies

        return {
            "staff_id": staff_id,
            "role_name": staff.role.name if staff.role else None,
            "role_permissions": list(role_permissions),
            "override_grants": list(override_grants),
            "override_denies": list(override_denies),
            "final_permissions": list(final_permissions),
            "overrides_detail": [
                {
                    "permission": o.permission.name,
                    "granted": o.granted,
                    "reason": o.reason,
                    "expires_at": o.expires_at.isoformat() if o.expires_at else None,
                }
                for o in overrides
            ],
        }

    @staticmethod
    def grant_permission_override(
        db: Session,
        staff_id: UUID,
        permission_name: str,
        reason: Union[str, None] = None,
        expires_at: Union[datetime, None] = None,
    ) -> bool:
        """Grant a specific permission to a staff member"""
        permission = (
            db.query(Permission).filter(Permission.name == permission_name).first()
        )
        if not permission:
            return False

        # Remove any existing override for this permission
        db.query(StaffPermissionOverride).filter(
            StaffPermissionOverride.staff_id == staff_id,
            StaffPermissionOverride.permission_id == permission.id,
        ).delete()

        # Add new grant override
        override = StaffPermissionOverride(
            staff_id=staff_id,
            permission_id=permission.id,
            granted=True,
            reason=reason,
            expires_at=expires_at,
        )

        db.add(override)
        db.commit()

        return True

    @staticmethod
    def deny_permission_override(
        db: Session,
        staff_id: UUID,
        permission_name: str,
        reason: Union[str, None] = None,
        expires_at: Union[datetime, None] = None,
    ) -> bool:
        """Deny a specific permission for a staff member"""
        permission = (
            db.query(Permission).filter(Permission.name == permission_name).first()
        )
        if not permission:
            return False

        # Remove any existing override for this permission
        db.query(StaffPermissionOverride).filter(
            StaffPermissionOverride.staff_id == staff_id,
            StaffPermissionOverride.permission_id == permission.id,
        ).delete()

        # Add new deny override
        override = StaffPermissionOverride(
            staff_id=staff_id,
            permission_id=permission.id,
            granted=False,
            reason=reason,
            expires_at=expires_at,
        )

        db.add(override)
        db.commit()

        return True

    @staticmethod
    def remove_permission_override(
        db: Session, staff_id: UUID, permission_name: str
    ) -> bool:
        """Remove any override for a specific permission (revert to role default)"""
        permission = (
            db.query(Permission).filter(Permission.name == permission_name).first()
        )
        if not permission:
            return False

        deleted = (
            db.query(StaffPermissionOverride)
            .filter(
                StaffPermissionOverride.staff_id == staff_id,
                StaffPermissionOverride.permission_id == permission.id,
            )
            .delete()
        )

        db.commit()

        return deleted > 0

    @staticmethod
    def cleanup_expired_overrides(db: Session):
        """Remove expired permission overrides"""
        deleted = (
            db.query(StaffPermissionOverride)
            .filter(StaffPermissionOverride.expires_at < datetime.utcnow())
            .delete()
        )

        db.commit()

        return deleted

    @staticmethod
    def has_permission(db: Session, staff_id: UUID, permission: str) -> bool:
        """Check if staff has specific permission"""
        permissions = PermissionService.get_staff_permissions(db, staff_id)
        return permission in permissions

    @staticmethod
    def has_any_permission(db: Session, staff_id: UUID, permissions: List[str]) -> bool:
        """Check if staff has any of the given permissions"""
        staff_permissions = PermissionService.get_staff_permissions(db, staff_id)
        return any(perm in staff_permissions for perm in permissions)

    @staticmethod
    def has_all_permissions(
        db: Session, staff_id: UUID, permissions: List[str]
    ) -> bool:
        """Check if staff has all given permissions"""
        staff_permissions = PermissionService.get_staff_permissions(db, staff_id)
        return all(perm in staff_permissions for perm in permissions)

    @staticmethod
    def can(db: Session, staff_id: UUID, action: str, resource: str) -> bool:
        """Check if user can perform action on resource"""
        permission = f"{resource}.{action}"
        return PermissionService.has_permission(db, staff_id, permission)


permission_service = PermissionService()
