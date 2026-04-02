import uuid

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class BlogBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class BlogResponse(BlogBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
class BlogCreateResponse(BaseModel):
    blog: BlogResponse
    task_id: Optional[str] = None
    
class BlogUpdateResponse(BaseModel):
    blog: BlogResponse
    task_id: Optional[str] = None