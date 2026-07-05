import uuid

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class BlogBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    summary: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = None
    is_private: Optional[bool] = False
    
    
class BlogCreate(BlogBase):
    pass
    

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    is_private: Optional[bool] = False
    is_locked: Optional[bool] = False
    is_archived: Optional[bool] = False
    

class BlogAdminUpdate(BlogUpdate):
    is_deleted: Optional[bool] = False
    is_featured: Optional[bool] = False
    

class BlogInDB(BlogBase):
    id: str
    user_id: str
    slug: str
    status: str
    

class BlogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    slug: str

    status: str
    published_at: Optional[datetime]

    summary: Optional[str]
    cover_image: Optional[str]
    reading_time: Optional[int]

    view_count: int
    like_count: int
    comment_count: int
    bookmark_count: int

    is_featured: bool
    is_private: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
        
class BlogAdminResponse(BlogResponse):
    is_locked: bool
    is_archived: bool
    is_deleted: bool
    
class BlogListResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    summary: Optional[str]
    cover_image: Optional[str]

    view_count: int
    like_count: int

    is_deleted: bool
    
    published_at: Optional[datetime]

    class Config:
        from_attributes = True
        

class BlogPublishRequest(BaseModel):
    status: str