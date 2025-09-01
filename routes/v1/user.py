import os
from typing import Annotated, Sequence
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import get_current_active_user
from crud.token_blacklist import token_blacklist_crud
from crud.user import user_crud
from database.database import get_db
from models.user import User
from schemas.errors import ErrorOut
from schemas.users import (
    ChangePassword,
    LoginResponse,
    RefreshTokenBody,
    ResetPassword,
    Token,
    UserCreate,
    UserLogin,
    UserOut,
    UserRegisterResponse,
    UserUpdate,
)
from schemas.utils import GenericResponse
from services.auth import user_auth_service
from services.image_config import image_service
from services.mail import email_service

user_router = APIRouter()


@user_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={201: {"model": UserRegisterResponse}, 409: {"model": ErrorOut}},
)
async def create_user(
    user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    new_user = user_crud.create_user(db, user)
    token = user_auth_service.login_user(new_user)

    background_tasks.add_task(
        email_service.send_email,
        email=new_user.email,
        subject="Welcome to ReTaler",
        body=(
            f"Hello {new_user.username}\n\n"
            "Welcome to ReTaler),\n\n"
            "Thank you for registering with ReTaler! We're excited to have you on board.\n\n"
            "Best regards,\nReTaler Team"
        ),
    )
    # token = user_auth_service.login_user(new_user)
    return {"detail": "User created successfully", "user": new_user, "token": token}


# TODO: remove this endpoint for data privacy
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=Sequence[UserOut])
async def get_all_users(db: Session = Depends(get_db)):
    all_users = user_crud.get_users(db)
    return all_users


@user_router.patch(
    "/{user_id}/update",
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user_update = user_crud.update_user(db, user_id, user_update)
    return user_update


@user_router.get("/{user_id}")
async def get_all_user_details(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not exists"
        )

    response = {}
    response["user"] = user

    user.stores
    user.staff_profile
    for profile in user.staff_profile:
        profile.role

    return response


@user_router.post(
    "/login", response_model=LoginResponse, status_code=status.HTTP_200_OK
)
async def login_user(
    user_login: UserLogin,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = user_auth_service.authenticate_user(
        db, user_login.email, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = user_auth_service.login_user(user)
    background_tasks.add_task(
        email_service.send_email,
        email=user.email,
        subject="Login Notification",
        body=(
            f"Hello {user.username},\n\n"
            "You have successfully logged in to your ReTaler account.\n\n"
            "Best regards,\nReTaler Team"
        ),
    )
    return {
        "user": user,
        "token": token,
    }


@user_router.patch(
    "/reset-password",
    status_code=status.HTTP_201_CREATED,
    responses={201: {"model": GenericResponse}, 404: {"model": ErrorOut}},
)
async def reset_password(
    user: ResetPassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # code to check if user exits already , if user exits continue, if not error user does not exist.
    user = user_crud.get_user_by_email(db, user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    reset_token = user_auth_service.generate_reset_token(user)
    reset_link = (
        f"{os.getenv("FRONTEND_URL")}/reset_password?token={reset_token.access_token}"
    )
    background_tasks.add_task(
        email_service.send_email,
        email=user.email,
        subject="ReTaler: Password reset request",
        body=(
            f"Hello {user.username},\n\n"
            "Someone (hopefully you) requested a password reset for your ReTaler account.\n\n"
            "If you made this request, please click the link below to reset your password:\n\n"
            f"{reset_link}\n\n\n"
            "This link will expire in 30 minutes for your security.\n"
            "If you didn't request a password reset, you can safely ignore this email.\n\n"
            "Best regards,\n"
            "The ReTaler Team,\n"
        ),
    )
    return {
        "status_code": status.HTTP_201_CREATED,
        "detail": "Password Reset Link Sent to your email",
    }


@user_router.patch(
    "/change-password",
    status_code=status.HTTP_200_OK,
    responses={200: {"model": GenericResponse}, 400: {"model": ErrorOut}},
)
async def change_password(
    user_details: ChangePassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    user_crud.update_password(db, user, user_details.password)
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "Password changed successfully.",
    }


@user_router.post("/token", response_model=Token)
async def user_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = user_auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = user_auth_service.login_user(user)

    return token


@user_router.post("/upload-profile-image", status_code=status.HTTP_200_OK)
async def upload_user_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    # Upload to Cloudinary
    image_url = await image_service.validate_and_upload_profile_picture(
        file, str(user.id)
    )

    # Update user record
    user_crud.update_user_picture(db, user, image_url)

    return {"detail": "Profile image uploaded successfully", "image_url": image_url}


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={200: {"model": GenericResponse}, 404: {"model": ErrorOut}},
)
async def delete_user_account(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user = user_crud.get_user_by_id(db, user_id)
    # Prevent deleting another user's account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this account",
        )
    user_crud.delete_user(db, user_id)
    return {"detail": "User deleted successfully", "status_code": status.HTTP_200_OK}


@user_router.post("/token/refresh", response_model=Token)
async def refresh_token(
    tokens: RefreshTokenBody,
    db: Session = Depends(get_db),
):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token_blacklist_crud.get_token(db, tokens.refresh_token):
        raise invalid_token_exception

    user = user_auth_service.get_user_from_token(db, tokens.refresh_token)
    if not user:
        raise invalid_token_exception

    # Ensure the access token matches the user
    user_from_access_token = user_auth_service.get_user_from_token(
        db, tokens.access_token
    )
    if not user_from_access_token or user.email != user_from_access_token.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not match user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_blacklist_crud.add_tokens(db, [tokens.access_token, tokens.refresh_token])

    new_token = user_auth_service.login_user(user)
    return new_token
