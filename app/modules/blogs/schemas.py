import uuid

from pydantic import BaseModel
from typing import Optional


class BlogBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class BlogResponse(BlogBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True