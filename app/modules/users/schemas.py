from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.modules.blogs.schemas import BlogResponse


class UserBase(BaseModel):
    username: Optional[str] = None
    profile_image: Optional[str] = None
    profile_bio: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str
    is_email_verified: bool = False


class UserInfo(UserBase):
    is_email_verified: bool
    is_admin: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInfo):
    id: UUID
    email: EmailStr
    blogs: List[BlogResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(BaseModel):
    user: UserResponse
    task_id: Optional[str] = None


class UserUpdateResponse(BaseModel):
    user : UserResponse
    task_id: Optional[str] = None