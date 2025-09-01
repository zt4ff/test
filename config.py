import os
import uuid
from datetime import datetime, timedelta
from typing import Annotated, List

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.token_blacklist import token_blacklist_crud
from crud.user import user_crud
from database.database import get_db
from models.staff import Staff
from models.store import Store
from schemas.users import TokenData, UserOut
from services.permission import permission_service

load_dotenv()
# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 1440))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = {
        key: str(value) if isinstance(value, (uuid.UUID)) else value
        for key, value in data.items()
    }
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = {
        key: str(value) if isinstance(value, (uuid.UUID)) else value
        for key, value in data.items()
    }
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token_blacklist_crud.get_token(db, token):
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserOut = Depends(get_current_user)):
    if current_user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_staff(
    store_id: Annotated[uuid.UUID, Path(title="store id")],
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    # Check if the user is a staff member of the store
    staff = db.scalar(
        select(Staff).where(
            Staff.store_id == store_id, Staff.user_id == current_user.id
        )
    )
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not a staff"
        )
    elif not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Staff is not active"
        )
    return staff


# ============ Used for authorization based on roles ===============
# Permission dependency factory
def require_permission(permission: str):
    """Dependency factory for single permission"""

    def permission_dependency(
        current_staff: Staff = Depends(get_current_staff), db: Session = Depends(get_db)
    ):
        if not permission_service.has_permission(db, current_staff.id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {permission}",
            )
        return current_staff

    return permission_dependency


def require_any_permission(permissions: List[str]):
    """Dependency factory for multiple permissions (need any one)"""

    def permission_dependency(
        current_staff: Staff = Depends(get_current_staff), db: Session = Depends(get_db)
    ):
        if not permission_service.has_any_permission(db, current_staff.id, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required any of: {', '.join(permissions)}",
            )
        return current_staff

    return permission_dependency


def require_all_permissions(permissions: List[str]):
    """Dependency factory for multiple permissions (need all)"""

    def permission_dependency(
        current_staff: Staff = Depends(get_current_staff), db: Session = Depends(get_db)
    ):
        if not permission_service.has_all_permissions(
            db, current_staff.id, permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required all of: {', '.join(permissions)}",
            )
        return current_staff

    return permission_dependency


def can_access_resource(action: str, resource: str):
    """Dependency factory for resource-action based permissions"""

    def permission_dependency(
        current_staff: Staff = Depends(get_current_staff), db: Session = Depends(get_db)
    ):
        if not permission_service.can(db, current_staff.id, action, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Cannot {action} {resource}",
            )
        return current_staff

    return permission_dependency


# def require_store_owner_or_staff_with_permission(permission: str):
#     """
#     Allows access if:
#     - User is the store owner (created_by), OR
#     - User is an active staff member with the given permission
#     """
#     def dependency(
#         store_id: uuid.UUID = Path(..., title="Store ID"),
#         db: Session = Depends(get_db),
#         current_user: UserOut = Depends(get_current_active_user),
#     ):
#         result = db.execute(
#             select(Store.created_by, Staff.id, Staff.is_active)
#             .outerjoin(Staff, (Staff.store_id == Store.id) & (Staff.user_id == current_user.id))
#             .where(Store.id == store_id)
#         ).fetchone()

#         if not result:
#             raise HTTPException(status_code=404, detail="Store not found")

#         created_by, staff_id, staff_is_active = result

#         # Store owner
#         if created_by == current_user.id:
#             return current_user

#         # Staff checks
#         if not staff_id:
#             raise HTTPException(status_code=403, detail="User is neither store owner nor a staff member")
#         if not staff_is_active:
#             raise HTTPException(status_code=403, detail="Staff account is not active")

#         if not permission_service.has_permission(db, staff_id, permission):
#             raise HTTPException(status_code=403, detail=f"Missing required permission: {permission}")

#         return current_user

#     return dependency
