import os
from datetime import timedelta
from uuid import UUID

from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import create_access_token, create_refresh_token
from dependencies.auth import get_password_hash, verify_password
from models.user import User
from schemas.store import StoreInvite
from schemas.users import Token

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 1440))

load_dotenv()
# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


class AuthService:

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email, User.is_active == True).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
          raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )
        return user

    @staticmethod
    def login_user(user: User) -> Token:
        data = {"sub": user.email, "id": user.id}
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data, access_token_expires)
        refresh_token = create_refresh_token(data, refresh_token_expires)
        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def generate_reset_token(user: User) -> Token:
        data = {"sub": user.email, "id": user.id}
        reset_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        reset_token = create_access_token(data=data, expires_delta=reset_token_expires)
        return Token(access_token=reset_token)

    @staticmethod
    def update_password(db: Session, user: User, password: str) -> Token:
        user.password_hash = get_password_hash(password)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_from_token(db: Session, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
        except JWTError:
            return None
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def generate_invitation_token(store_invite: StoreInvite) -> Token:
        data = {
            "store_id": store_invite.store_id,
            "email": store_invite.staff_email,
            "role": store_invite.role,
        }
        invitation_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        invitation_token = create_access_token(
            data=data, expires_delta=invitation_token_expires
        )
        return Token(access_token=invitation_token)

    @staticmethod
    def get_staff_from_invite_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str | None = payload.get("email")
            store_id: UUID | None = payload.get("store_id")
            role: str | None = payload.get("role")
            if email is None:
                return None
        except JWTError:
            return None
        return {"email": email, "role": role, "store_id": store_id}

    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        import random
        import string
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))


user_auth_service = AuthService()
