import os
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from config import (
    get_current_active_user,
    get_current_staff,
    require_any_permission,
    require_permission,
)
from crud.role import role_crud
from crud.staff import staff_crud
from crud.store import store_crud
from crud.user import user_crud
from database.database import get_db
from models.staff import Staff, StaffStatus
from models.user import User
from schemas.errors import ErrorOut
from schemas.staff import (
    StaffAdd,
    StaffCreate,
    StaffCreateOut,
    StaffData,
    StaffDetail,
    StaffGenericResponseWithStaffData,
    StaffsData,
    StaffUpdate,
)
from schemas.store import (
    StoreAcceptInvite,
    StoreCreate,
    StoreGenericResponseWithStoreData,
    StoreInvite,
    StoreInviteResend,
)
from schemas.users import UserCreate
from schemas.utils import GenericResponse
from services.auth import user_auth_service
from services.mail import email_service

store_router = APIRouter()


@store_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": StoreGenericResponseWithStoreData},
        400: {"model": ErrorOut},
    },
)
async def create_store(
    store_data: StoreCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    store = store_crud.create_store(db, user, store_data)
    background_tasks.add_task(
        email_service.send_email,
        email=user.email,
        subject="Store Created",
        body=(
            f"Hello {user.username},\n\n"
            f"You have successfully created {store.name}.\n\n"
            "Best regards,\nReTaler Team"
        ),
    )

    return {
        "store": store,
        "status_code": status.HTTP_201_CREATED,
        "detail": "Store created successfully",
    }


@store_router.get(
    "/",
    responses={
        404: {"model": ErrorOut},
        200: {"model": StoreGenericResponseWithStoreData},
    },
)
async def get_user_stores(user: User = Depends(get_current_active_user)):
    stores = user.stores
    if not stores:
        return HTTPException(
            status.HTTP_404_NOT_FOUND, "user does not have a registered store"
        )

    return {
        "stores": stores,
        "status_code": status.HTTP_200_OK,
        "detail": "Stores retrieved successfully",
    }


@store_router.get(
    "/{store_id}/debug-staff-status",
    responses={
        200: {"model": dict},
        404: {"model": ErrorOut},
    },
)
async def debug_staff_status(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Debug endpoint to check current user's staff status in a store."""
    from sqlalchemy import select

    from models.staff import Staff
    from models.store import Store

    # Check if store exists
    store = db.scalar(select(Store).where(Store.id == store_id))
    store_exists = store is not None

    # Check if user is staff in this store
    staff = db.scalar(
        select(Staff).where(
            Staff.store_id == store_id, Staff.user_id == current_user.id
        )
    )

    # Get all staff records for this user
    all_user_staff = db.scalars(
        select(Staff).where(Staff.user_id == current_user.id)
    ).all()

    return {
        "current_user_id": str(current_user.id),
        "current_user_email": current_user.email,
        "store_id": str(store_id),
        "store_exists": store_exists,
        "store_name": store.name if store else None,
        "is_staff_in_store": staff is not None,
        "staff_status": staff.status.value if staff else None,
        "staff_is_active": staff.is_active if staff else None,
        "staff_role": staff.role.name if staff and staff.role else None,
        "all_user_staff_stores": [
            {
                "store_id": str(s.store_id),
                "status": s.status.value,
                "is_active": s.is_active,
                "role": s.role.name if s.role else None,
            }
            for s in all_user_staff
        ],
    }


@store_router.post(
    "/{store_id}/staff",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": StaffGenericResponseWithStaffData},
        404: {"model": ErrorOut},
        403: {"model": ErrorOut},
    },
)
async def add_staff(
    store_id: UUID,
    staff_data: StaffAdd,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(
        require_any_permission(["staff.create", "staff.invite"])
    ),
):
    """Add a new staff member to the store."""
    store = store_crud.get_store_by_id(db, store_id)

    if store.id != current_staff.store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add staff to this store",
        )

    if not current_staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Staff is not active"
        )

    existing_user = db.query(User).filter(User.email == staff_data.email).first()
    password = ""
    if not existing_user:
        password = user_auth_service.generate_random_password()
        existing_user = user_crud.create_user(
            db,
            UserCreate(
                email=staff_data.email,
                username=staff_data.email.split("@")[0],
                password=password,
            ),
            True,
        )

    new_staff = staff_crud.get_staff_by_user_id(db, store_id, existing_user.id)
    if not new_staff:
        new_staff = staff_crud.create_staff(
            db,
            StaffCreate(
                role=staff_data.role, user_id=existing_user.id, store_id=store_id
            ),
            StaffStatus.PENDING,
        )

    if new_staff.status == StaffStatus.PENDING:
        invite = StoreInvite(
            staff_email=existing_user.email, store_id=store_id, role=staff_data.role
        )
        intivation_token = user_auth_service.generate_invitation_token(invite)
        invite_link = f"{os.getenv("FRONTEND_URL")}{intivation_token.access_token}"

        login_info = (
            f"<br/>Email: {existing_user.email}\n<br/>" f"Password: {password}<br/>\n\n"
            if password
            else ""
        )

        background_tasks.add_task(
            email_service.send_email,
            email=existing_user.email,
            subject=f"ReTaler: {store.name} invitation",
            body=(
                f"Hello {staff_data.email.split("@")[0].upper()},\n\n"
                f"<b>{current_staff.user.username.upper()}</b> is inviting you to join their store.\n\n"
                "Please click the link below to get onboarded:\n\n"
                f"{invite_link}\n\n"
                f"{login_info}"
                "This link will expire in 30 minutes.\n"
                "If you're not sure who it is from, you can safely ignore this email.\n\n"
                "Best regards,\n"
                "The ReTaler Team,\n"
            ),
        )
    else:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff already exists and is not in pending status",
        )

    staff = StaffCreateOut(
        id=new_staff.id,
        role=staff_data.role,
        role_id=new_staff.role_id,
        user_id=new_staff.user_id,
        store_id=store_id,
        status=new_staff.status,
    )
    return StaffGenericResponseWithStaffData(
        status_code=status.HTTP_201_CREATED,
        data=jsonable_encoder(staff),
        detail="Staff invitation sent successfully",
    )


@store_router.post(
    "/{store_id}/staff/resend-invitation",
    responses={
        200: {"model": GenericResponse},
        400: {"model": ErrorOut},
        403: {"model": ErrorOut},
        404: {"model": ErrorOut},
    },
)
async def resend_invitation_email(
    store_id: UUID,
    store_invite: StoreInviteResend,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("staff.invite")),
):
    """Resend invitation email to staff."""
    staff = staff_crud.get_staff_by_id(db, store_invite.staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found"
        )
    elif staff.status != StaffStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff is not in pending status",
        )

    store = store_crud.get_store_by_id(db, store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store not found"
        )

    if store.id != staff.store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to resend invitation for this store",
        )

    invite = StoreInvite(
        staff_email=staff.user.email, store_id=store_id, role=staff.role.name
    )
    intivation_token = user_auth_service.generate_invitation_token(invite)
    invite_link = f"{os.getenv("FRONTEND_URL")}/accept-invitation?token={intivation_token.access_token}"

    background_tasks.add_task(
        email_service.send_email,
        email=staff.user.email,
        subject=f"ReTaler: {store.name} invitation",
        body=(
            f"Hello {staff.user.email.split('@')[0].upper()},\n\n"
            f"<b>{current_staff.user.username.upper()}</b> is inviting you to join their store.\n\n"
            "Please click the link below to get onboarded:\n\n"
            f"{invite_link}\n\n"
            "This link will expire in 30 minutes.\n"
            "If you're not sure who it is from, you can safely ignore this email.\n\n"
            "Best regards,\n"
            "The ReTaler Team,\n"
        ),
    )

    return GenericResponse(
        status_code=status.HTTP_200_OK, detail="Invitation email resent successfully"
    )


@store_router.post(
    "/accept-invitation",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": StaffGenericResponseWithStaffData},
        401: {"model": ErrorOut},
    },
)
async def accept_store_invitation(
    token: str,
    user_data: StoreAcceptInvite,
    background_task: BackgroundTasks,
    db: Session = Depends(get_db),
):
    staff_details = user_auth_service.get_staff_from_invite_token(token)
    if staff_details == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    email = staff_details.get("email")
    store_id = staff_details.get("store_id")
    role = staff_details.get("role")

    user = user_crud.get_user_by_email(db, email)
    if user is None:
        user = user_crud.create_user(
            db,
            UserCreate(
                email=email, username=user_data.username, password=user_data.password
            ),
        )

    new_staff = staff_crud.get_staff_by_user_id(db, store_id, user.id)

    if new_staff is None:
        new_staff = staff_crud.create_staff(
            db,
            StaffCreate(role=role, user_id=user.id, store_id=store_id),
            StaffStatus.ACTIVE,
        )
    elif new_staff.status != StaffStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff already exists and is not in pending status",
        )
    else:
        new_staff.status = StaffStatus.ACTIVE
        db.commit()
        db.refresh(new_staff)

    background_task.add_task(
        email_service.send_email,
        email=user.email,
        subject=f"ReTaler: store invitation accepted",
        body=(
            f"Hello {user.username.upper()},\n\n"
            f"You are now part of a new store.\n\n"
            "If this is an error, please report using the link below:\n\n"
            f"{os.getenv("FRONTEND_URL")}/report\n\n"
            "Best regards,\n"
            "The ReTaler Team,\n"
        ),
    )

    return StaffGenericResponseWithStaffData(
        status_code=status.HTTP_201_CREATED,
        detail="staff created",
        data=jsonable_encoder(new_staff),
    )


@store_router.patch(
    "/{store_id}/staff",
    responses={
        200: {"model": StaffGenericResponseWithStaffData},
        403: {"model": ErrorOut},
        404: {"model": ErrorOut},
    },
)
async def update_staff(
    store_id: UUID,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(require_permission("roles.manage")),
):
    """Update the status of a staff member."""
    store = store_crud.get_store_by_id(db, store_id)
    staff = staff_crud.get_staff_by_id(db, staff_data.staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found"
        )

    if staff.store_id != store.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this staff member",
        )

    for field, value in staff_data.model_dump(exclude_unset=True).items():
        if field == "role":
            staff = role_crud.grant_role(db, staff, value)
        elif field == "status":
            if value is not None and value not in StaffStatus:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid staff status",
                )
            staff.status = staff_data.status.value

    db.commit()
    db.refresh(staff)

    return StaffGenericResponseWithStaffData(
        status_code=status.HTTP_200_OK,
        detail="Staff status updated successfully",
        data=jsonable_encoder(staff),
    )


@store_router.get(
    "/{store_id}/staff",
    responses={
        200: {"model": StaffsData},
        404: {"model": ErrorOut},
    },
)
async def get_store_staffs(
    store_id: UUID,
    db: Session = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    """Get all staff members of a store."""
    staffs = staff_crud.get_all_store_staffs(db, store_id)
    if not staffs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No staff found for this store",
        )

    data = []
    for staff in staffs:
        data.append(
            StaffDetail(
                id=staff.id,
                user_id=staff.user_id,
                store_id=staff.store_id,
                status=staff.status,
                role=staff.role_name,
                name=staff.user.username,
                phone_no=None,
                email=staff.user.email,
                login_time="09:00:00 AM",
                logout_time="06:00:00 PM",
            )
        )

    return StaffsData(
        status_code=status.HTTP_200_OK,
        detail="Staffs retrieved successfully",
        data=jsonable_encoder(data),
    )


@store_router.get(
    "/{store_id}/staff/{staff_id}",
    responses={
        200: {"model": StaffData},
        404: {"model": ErrorOut},
    },
)
async def get_staff_details(
    store_id: UUID,
    staff_id: UUID,
    db: Session = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    """Get the detail of a staff member of the store."""
    staff = staff_crud.get_staff_by_id(db, staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="staff not found",
        )

    data = StaffDetail(
        id=staff.id,
        user_id=staff.user_id,
        store_id=staff.store_id,
        status=staff.status,
        role=staff.role_name,
        name=staff.user.username,
        phone_no=None,
        email=staff.user.email,
        login_time="09:00:00 AM",
        logout_time="06:00:00 PM",
    )

    return StaffData(
        status_code=status.HTTP_200_OK,
        detail="Staffs retrieved successfully",
        data=jsonable_encoder(data),
    )
