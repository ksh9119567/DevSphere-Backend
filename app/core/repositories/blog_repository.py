import logging

from sqlalchemy.future import select

from .base_repository import BaseRepository

from app.modules.blogs.models import Blog

logger = logging.getLogger(__name__)


class BlogRepository(BaseRepository):

    async def create_blog(self, blog: Blog) -> Blog:
        logger.debug(f"Creating blog: {blog.title} for user_id: {blog.user_id}")
        blog = await self.create(blog)
        logger.info(f"Blog created successfully with id: {blog.id}")
        return blog

    async def get_user_blogs(self, user_id: int) -> list[Blog]:
        logger.debug(f"Fetching blogs for user_id: {user_id}")

        query = select(Blog).filter(
            Blog.user_id == user_id,
            Blog.is_deleted == False
        )

        return await self.get_all(query)

    async def get_all_blogs(self) -> list[Blog]:
        logger.debug("Fetching all blogs")

        query = select(Blog).filter(Blog.is_deleted == False)

        return await self.get_all(query)

    async def get_blog_by_id(self, blog_id: int) -> Blog:
        logger.debug(f"Fetching blog by id: {blog_id}")

        query = select(Blog).filter(
            Blog.id == blog_id,
            Blog.is_deleted == False
        )

        return await self.get_one(query)

    async def get_user_blog_by_id(self, blog_id: int, user_id: int) -> Blog:
        logger.debug(f"Fetching blog - id: {blog_id}, user_id: {user_id}")

        query = select(Blog).filter(
            Blog.id == blog_id,
            Blog.user_id == user_id,
            Blog.is_deleted == False
        )

        return await self.get_one(query)

    async def update_blog(self, blog: Blog) -> Blog:
        logger.debug(f"Updating blog: {blog.id}")
        blog = await self.update(blog)
        logger.info(f"Blog updated successfully: {blog.id}")
        return blog

    async def delete_blog(self, blog: Blog) -> None:
        logger.debug(f"Deleting blog: {blog.id}")

        await self.soft_delete(blog, {"is_deleted": True})

        logger.info(f"Blog deleted successfully: {blog.id}")