from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID

from app.modules.blogs.schemas import BlogResponse


class UserBase(BaseModel):
    username: Optional[str] = None
    profile_image: Optional[str] = None
    profile_bio: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserInfo(UserBase):
    is_email_verified: bool
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True

class UserResponse(UserInfo):
    id: UUID
    email: EmailStr
    blogs: List[BlogResponse] = []
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True

class UserCreateResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"