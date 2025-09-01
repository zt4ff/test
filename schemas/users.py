from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class ResetPassword(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    password: str
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = "Admin"


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class RefreshTokenBody(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    email: str | None = None


class UserOut(UserBase):
    id: UUID
    is_active: bool = True
    role: str = "Admin"
    is_active: bool 
    profile_picture_url: str | None = None
   

    model_config = {"from_attributes": True}



class LoginResponse(BaseModel):
    user: UserOut
    token: Token


class UserRegisterResponse(BaseModel):
    detail: str
    user: UserOut
    token: Token
