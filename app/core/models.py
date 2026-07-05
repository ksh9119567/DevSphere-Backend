from datetime import datetime, timezone
from sqlalchemy import Column, DateTime


class TimestampMixin:
    """
    Timestamps for created_at and updated_at
    """
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    class Config:
        orm_mode = True