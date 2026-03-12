from datetime import datetime, timezone
from sqlalchemy import Column, DateTime


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)

    class Config:
        orm_mode = True