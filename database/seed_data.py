from sqlalchemy.orm import Session

from database.database import SessionLocal
from models.role import Permission, Role


def seed_data():
    """Seed initial data"""
    db: Session = SessionLocal()
    # Create permissions
    permissions_data = [
        ("products.view", "products", "view"),
        ("products.create", "products", "create"),
        ("products.edit", "products", "edit"),
        ("products.delete", "products", "delete"),
        ("sales.view", "sales", "view"),
        ("sales.create", "sales", "create"),
        ("sales.delete", "sales", "delete"),
        ("sales.edit", "sales", "edit"),
        ("staff.view", "staff", "view"),
        ("staff.create", "staff", "create"),
        ("staff.invite", "staff", "invite"),
        ("staff.delete", "staff", "delete"),
        ("roles.manage", "roles", "manage"),
        ("analytics.view", "analytics", "view"),
    ]

    permissions = []
    for name, resource, action in permissions_data:
        perm = db.query(Permission).filter(Permission.name == name).first()
        if not perm:
            perm = Permission(name=name, resource=resource, action=action)
            db.add(perm)
            db.commit()
        permissions.append(perm)

    # Create roles
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if not admin_role:
        admin_role = Role(name="Admin", description="Full access")
        admin_role.permissions = permissions  # Give all permissions
        db.add(admin_role)

    manager_role = db.query(Role).filter(Role.name == "Manager").first()
    if not manager_role:
        manager_role = Role(name="Manager", description="Limited management access")
        # Give subset of permissions
        manager_permissions = [
            p
            for p in permissions
            if p.name
            in [
                "products.view",
                "products.create",
                "products.edit",
                "sales.view",
                "sales.create",
                "sales.edit",
                "analytics.view",
            ]
        ]
        manager_role.permissions = manager_permissions
        db.add(manager_role)

    sales_rep_role = db.query(Role).filter(Role.name == "Sales Rep").first()
    if not sales_rep_role:
        sales_rep_role = Role(name="Sales Rep", description="Limited Sales access")
        # Give subset of permissions
        sales_rep_permissions = [
            p
            for p in permissions
            if p.name
            in [
                "products.view",
                "sales.view",
                "sales.create",
                "analytics.view",
            ]
        ]
        sales_rep_role.permissions = sales_rep_permissions
        db.add(sales_rep_role)

    db.commit()
