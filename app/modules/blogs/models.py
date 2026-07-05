import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column, DateTime, Integer, String, Text, ForeignKey, 
    Boolean, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.core.models import TimestampMixin


class Blog(Base, TimestampMixin):
    __tablename__ = "blogs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # URL
    slug = Column(String(255), nullable=False) # URL-friendly identifier generated from title
    
    # Publishing status
    status = Column(String(20), default="draft")  # draft / published / scheduled / archived
    published_at = Column(DateTime, nullable=True) # when the blog was published
    
    # Content metadata
    summary = Column(String(500), nullable=True) # short summary
    cover_image = Column(String(255), nullable=True) # URL of the cover image
    reading_time = Column(Integer, nullable=True)  # estimated reading time in minutes
    
    # Engagement
    view_count = Column(Integer, default=0) # number of views
    like_count = Column(Integer, default=0) # number of likes
    comment_count = Column(Integer, default=0) # number of comments
    bookmark_count = Column(Integer, default=0) # number of bookmarks
    
    # Status fields
    is_deleted = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False) # whether the blog is featured on homepage
    is_locked = Column(Boolean, default=False)  # prevent edits    
    is_private = Column(Boolean, default=False) # only visible to the author and admins
    is_archived = Column(Boolean, default=False) # move to archive, not visible in normal listings
    
    # relationship
    creator = relationship("User", back_populates="blogs", lazy="selectin")
    likes = relationship("BlogLike", backref="blog", lazy="selectin")
    bookmarks = relationship("BlogBookmark", backref="blog", lazy="selectin")
    
    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="unique_user_blog_slug"),
        Index("ix_blogs_user_id", "user_id"),
    )
    
    
class BlogLike(Base, TimestampMixin):
    __tablename__ = "blog_likes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", 
                                                    name="fk_blog_likes_user_id_users"), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey("blogs.id", ondelete="CASCADE", 
                                                    name="fk_blog_likes_blog_id_blogs"), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("user_id", "blog_id", name="unique_user_blog_like"),
        Index("ix_blog_likes_user_id", "user_id"),
        Index("ix_blog_likes_blog_id", "blog_id"),
    )
    
    
class BlogBookmark(Base, TimestampMixin):
    __tablename__ = "blog_bookmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", 
                                                    name="fk_blog_bookmarks_user_id_users"),nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey("blogs.id", ondelete="CASCADE", 
                                                    name="fk_blog_bookmarks_blog_id_blogs"), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("user_id", "blog_id", name="unique_user_blog_bookmark"),
        Index("ix_blog_bookmarks_user_id", "user_id"),
        Index("ix_blog_bookmarks_blog_id", "blog_id"),
    )