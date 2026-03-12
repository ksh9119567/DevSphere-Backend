import logging
import uuid

from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Index

from app.db.database import Base

logger = logging.getLogger(__name__)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_email = Column(String(255), ForeignKey("users.email"), nullable=True, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False, index=True)
    action_description = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index("idx_user_timestamp", "user_email", "timestamp"),
        Index("idx_endpoint_timestamp", "endpoint", "timestamp"),
        Index("idx_status_timestamp", "status_code", "timestamp"),
    )

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_email={self.user_email}, endpoint={self.endpoint}, method={self.method}, status_code={self.status_code})>"
