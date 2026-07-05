from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.modules.blogs.schemas import BlogResponse


class UserBase(BaseModel):
    username: str = Field(..., max_length=100)
    display_name: Optional[str] = None
    profile_image: Optional[str] = None
    profile_bio: Optional[str] = Field(None, max_length=500)
    headline: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str
    is_email_verified: Optional[bool] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    profile_image: Optional[str] = None
    profile_bio: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    is_private_account: Optional[bool] = False


class UserAdminUpdate(UserUpdate):
    is_admin: Optional[bool] = False
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    is_verified: Optional[bool] = False
    is_suspended: Optional[bool] = False
    
class UserPublicResponse(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str]
    profile_image: Optional[str]
    profile_bio: Optional[str]
    headline: Optional[str]

    follower_count: int
    following_count: int

    is_verified: bool

    class Config:
        from_attributes = True
    

class UserPrivateResponse(UserPublicResponse):
    email: EmailStr
    location: Optional[str]
    website: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]

    is_private_account: bool
    is_email_verified: bool

    created_at: datetime
    updated_at: datetime
    

class UserAdminResponse(UserPrivateResponse):
    is_admin: bool
    is_active: bool
    is_deleted: bool
    is_suspended: bool
    is_verified: bool

    last_login: Optional[datetime]
    
    
class UserListResponse(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str]
    profile_image: Optional[str]

    follower_count: int
    
    is_active: Optional[bool]
    is_deleted: Optional[bool]

    class Config:
        from_attributes = True
        

class UserCreateResponse(BaseModel):
    user: UserPrivateResponse