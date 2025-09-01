from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import get_password_hash
from models.user import User
from schemas.users import UserCreate, UserUpdate


class UserCRUD:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate, is_active: bool = True) -> User:
        # Check if username exists
        existing_user = (
            db.query(User)
            .filter(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
            .first()
        )
        if existing_user:
            # If username is taken by active user → block
            if existing_user.username == user_data.username and existing_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists",
                )

            # If email exists
            if existing_user.email == user_data.email:
                if existing_user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already exists",
                    )
                # Reactivate with updated username & password
                existing_user.username = user_data.username
                existing_user.password_hash = get_password_hash(user_data.password)
                existing_user.is_active = True
                db.commit()
                db.refresh(existing_user)
                return existing_user
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            is_active=is_active,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get_users(db: Session):
        users = db.query(User).all()
        return users

    @staticmethod
    def get_user_by_id(db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active"
            )
        update_data = user_data.dict(exclude_unset=True)
        if "username" in update_data:
            existing = (
                db.query(User)
                .filter(User.username == update_data["username"], User.id != user_id)
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists",
                )
        if "email" in update_data:
            existing = (
                db.query(User)
                .filter(User.email == update_data["email"], User.id != user_id)
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
                )
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        return user

    @staticmethod
    def update_password(db: Session, user: User, new_password: str):
        # check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active"
            )
        user.password_hash = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user_picture(db: Session, user: User, picture_url: str):
        user.profile_picture_url = picture_url
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # Soft delete the user
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user


user_crud = UserCRUD()
