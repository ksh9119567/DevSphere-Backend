from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ActivityLogCreate(BaseModel):
    user_email: Optional[str]
    endpoint: str
    method: str
    status_code: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_body: Optional[str]
    response_body: Optional[str]
    response_time_ms: float
    action_description: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
        
        
class ActivityLogResponse(BaseModel):
    id: int
    user_email: Optional[str]
    endpoint: str
    method: str
    status_code: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    response_time_ms: float
    timestamp: datetime
    action_description: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class ActivityFilterParams(BaseModel):
    user_email: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0

    class Config:
        from_attributes = True
