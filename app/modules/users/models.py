import uuid

from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column, Integer, String, Boolean, Index, ForeignKey, 
    UniqueConstraint, CheckConstraint, DateTime
)
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.core.models import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    # Identity fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # Profile fields
    display_name = Column(String(100), nullable=False, default=username)
    profile_image = Column(String(255), nullable=True)
    profile_bio = Column(String(500), nullable=True)
    headline = Column(String(255), nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    linkedin = Column(String(100), nullable=True)
    github = Column(String(100), nullable=True)
    
    # Analytics fields
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)

    # System Fields
    last_login = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Status fields
    is_private_account = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)   # platform verified badge
    is_suspended = Column(Boolean, default=False)
    
    # relationship
    blogs = relationship("Blog", back_populates="creator", cascade="all, delete-orphan", lazy="selectin")
    liked_blogs = relationship("BlogLike", backref="user", lazy="selectin")
    bookmarked_blogs = relationship("BlogBookmark", backref="user", lazy="selectin")
    followers = relationship("UserFollow", foreign_keys="[UserFollow.following_id]",
                             backref="followed_user", lazy="selectin")
    following = relationship("UserFollow", foreign_keys="[UserFollow.follower_id]", 
                             backref="follower_user", lazy="selectin")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_admin={self.is_admin})>"
    
    
class UserFollow(Base, TimestampMixin):
    __tablename__ = "user_follows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", 
                                                        name="fk_user_follow_follower_id_users"), nullable=False)
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", 
                                                         name="fk_user_follow_following_id_users"), nullable=False)

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_user_follows_follower_following"),
        CheckConstraint("follower_id != following_id", name="ck_user_follows_no_self_follow"),
        Index("ix_user_follows_follower_id", "follower_id"),
        Index("ix_user_follows_following_id", "following_id"),
    )