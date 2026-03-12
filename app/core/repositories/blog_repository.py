import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.modules.blogs.models import Blog

logger = logging.getLogger(__name__)

class BlogRepository:
    @staticmethod
    async def create_blog(db: AsyncSession, blog: Blog) -> Blog:
        logger.debug(f"Creating blog: {blog.title} for user_id: {blog.user_id}")
        db.add(blog)
        await db.commit()
        await db.refresh(blog)
        logger.info(f"Blog created successfully with id: {blog.id}")
        return blog
    
    @staticmethod
    async def get_user_blogs(db: AsyncSession, user_id: int) -> list[Blog]:
        logger.debug(f"Fetching blogs for user_id: {user_id}")
        result = await db.execute(select(Blog).filter(Blog.user_id == user_id, Blog.is_deleted == False))
        return result.scalars().all()
    
    @staticmethod
    async def get_all_blogs(db: AsyncSession) -> list[Blog]:
        logger.debug("Fetching all blogs")
        result = await db.execute(select(Blog).filter(Blog.is_deleted == False))
        return result.scalars().all()
    
    @staticmethod
    async def get_blog_by_id(db: AsyncSession, blog_id: int) -> Blog:
        logger.debug(f"Fetching blog by id: {blog_id}")
        result = await db.execute(select(Blog).filter(Blog.id == blog_id, Blog.is_deleted == False))
        return result.scalars().first()
    
    @staticmethod
    async def get_user_blog_by_id(db: AsyncSession, blog_id: int, user_id: int) -> Blog:
        logger.debug(f"Fetching blog - id: {blog_id}, user_id: {user_id}")
        result = await db.execute(select(Blog).filter(Blog.id == blog_id, Blog.user_id == user_id, Blog.is_deleted == False))
        return result.scalars().first()
    
    @staticmethod
    async def update_blog(db: AsyncSession, blog: Blog) -> Blog:
        logger.debug(f"Updating blog: {blog.id}")
        await db.merge(blog)
        await db.commit()
        await db.refresh(blog)
        logger.info(f"Blog updated successfully: {blog.id}")
        return blog
    
    @staticmethod
    async def delete_blog(db: AsyncSession, blog: Blog) -> None:
        logger.debug(f"Deleting blog: {blog.id}")
        blog.is_deleted = True
        await db.merge(blog)
        await db.commit()
        logger.info(f"Blog deleted successfully: {blog.id}")
        
        