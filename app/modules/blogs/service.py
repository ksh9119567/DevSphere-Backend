import logging

from sqlalchemy.ext.asyncio import AsyncSession

from .models import Blog
from .schemas import BlogBase

from app.core.exception import NotFoundException
from app.core.repositories.user_repository import UserRepository
from app.core.repositories.blog_repository import BlogRepository

logger = logging.getLogger(__name__)

class BlogService:
    @staticmethod
    async def create_blog(request: BlogBase, user_id: int, db: AsyncSession) -> Blog:
        logger.info(f"Creating blog with title: '{request.title}' for user_id: {user_id}")
        new_blog = Blog(title=request.title, content=request.content, user_id=user_id)
        return await BlogRepository.create_blog(db, new_blog)

    @staticmethod
    async def get_user_blogs(user_id: int, db: AsyncSession) -> list[Blog]:
        logger.debug(f"Fetching blogs for user_id: {user_id}")
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found: user_id={user_id}")
            raise NotFoundException("User")
        
        blogs = await BlogRepository.get_user_blogs(db, user_id)
        if not blogs:
            logger.warning(f"No blogs found for user_id: {user_id}")
            raise NotFoundException("Blogs")
        return blogs

    @staticmethod
    async def get_all_blogs(db: AsyncSession) -> list[Blog]:
        logger.debug("Fetching all blogs")
        blogs = await BlogRepository.get_all_blogs(db)
        if not blogs:
            logger.warning("No blogs found in database")
            raise NotFoundException("Blogs")
        return blogs

    @staticmethod
    async def get_blog(blog_id: int, user_id: int, db: AsyncSession) -> Blog:
        logger.debug(f"Fetching blog_id: {blog_id} for user_id: {user_id}")
        blog = await BlogRepository.get_user_blog_by_id(db, blog_id, user_id)
        
        if not blog:
            logger.warning(f"Blog not found: blog_id={blog_id}, user_id={user_id}")
            raise NotFoundException("Blog")
        return blog
    
    @staticmethod
    async def update_blog(blog_id: int, request: BlogBase, user_id: int, is_admin: bool, db: AsyncSession) -> Blog:
        logger.info(f"Updating blog_id: {blog_id} for user_id: {user_id} (is_admin: {is_admin})")
        if is_admin:
            result = await BlogRepository.get_blog_by_id(db, blog_id)
        else:
            result = await BlogRepository.get_user_blog_by_id(db, blog_id, user_id)
        
        blog = result.scalars().first() if hasattr(result, 'scalars') else result
        if not blog:
            logger.warning(f"Blog not found for update: blog_id={blog_id}")
            raise NotFoundException("Blog")
        
        blog.title = request.title if request.title else blog.title
        blog.content = request.content if request.content else blog.content
        blog = await BlogRepository.update_blog(db, blog)
        logger.info(f"Blog updated successfully: blog_id={blog_id}")
        return blog

    @staticmethod
    async def delete_blog(blog_id: int, user_id: int, is_admin: bool, db: AsyncSession) -> str:
        logger.info(f"Deleting blog_id: {blog_id} for user_id: {user_id} (is_admin: {is_admin})")
        if is_admin:
            result = await BlogRepository.get_blog_by_id(db, blog_id)
        else:
            result = await BlogRepository.get_user_blog_by_id(db, blog_id, user_id)
        
        blog = result
        if not blog:
            logger.warning(f"Blog not found for deletion: blog_id={blog_id}")
            raise NotFoundException("Blog")
        
        await BlogRepository.delete_blog(db, blog)
        logger.info(f"Blog deleted successfully: blog_id={blog_id}")
        return "Blog deleted successfully"

