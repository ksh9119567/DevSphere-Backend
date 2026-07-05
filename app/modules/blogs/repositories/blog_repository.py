import logging

from sqlalchemy.future import select

from app.core.repository import BaseRepository
from app.core.exception import NotFoundException

from app.modules.blogs.models import Blog, BlogLike, BlogBookmark

logger = logging.getLogger(__name__)


class BlogRepository(BaseRepository):

    async def slug_exists(self, user_id, slug: str) -> bool:
        query = select(Blog).where(
            Blog.user_id == user_id,
            Blog.slug == slug,
            Blog.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_blog(self, 
                          blog: Blog) -> Blog:
        logger.debug(f"Creating blog: {blog.title} for user_id: {blog.user_id}")
        blog = await self.create(blog)
        logger.info(f"Blog created successfully with id: {blog.id}")
        return blog

    async def get_user_blogs(self, 
                             user_id: int) -> list[Blog]:
        logger.debug(f"Fetching blogs for user_id: {user_id}")

        query = select(Blog).filter(
            Blog.user_id == user_id,
            Blog.is_deleted == False
        )

        return await self.get_all(query)

    async def get_all_blogs(self) -> list[Blog]:
        logger.debug("Fetching all blogs")

        query = select(Blog)

        return await self.get_all(query)

    async def get_blog_by_id(self, 
                             blog_id: int) -> Blog:
        logger.debug(f"Fetching blog by id: {blog_id}")

        query = select(Blog).filter(
            Blog.id == blog_id
        )

        return await self.get_one(query)
    
    async def get_user_blog_by_id(self, 
                                  blog_id: int, 
                                  user_id: int) -> Blog:
        logger.debug(f"Fetching blog by id: {blog_id} for user_id: {user_id}")

        query = select(Blog).filter(
            Blog.id == blog_id,
            Blog.user_id == user_id,
            Blog.is_deleted == False
        )

        return await self.get_one(query)

    async def update_blog(self, 
                          blog: Blog) -> Blog:
        logger.debug(f"Updating blog: {blog.id}")
        blog = await self.update(blog)
        logger.info(f"Blog updated successfully: {blog.id}")
        return blog

    async def delete_blog(self, 
                          blog: Blog) -> None:
        logger.debug(f"Deleting blog: {blog.id}")

        await self.soft_delete(blog, {"is_deleted": True})

        logger.info(f"Blog deleted successfully: {blog.id}")
        
    async def delete_all_blogs(self, 
                               user_id: int) -> None:
        logger.debug(f"Deleting all blogs for user_id: {user_id}")

        query = select(Blog).filter(
            Blog.user_id == user_id,
            Blog.is_deleted == False
        )

        blogs = await self.get_all(query)

        for blog in blogs:
            await self.soft_delete(blog, {"is_deleted": True})
            
        logger.info(f"All blogs deleted successfully for user_id: {user_id}")
        
    async def like_blog(self, 
                        blog_like: BlogLike) -> BlogLike:
        # Fetch the blog
        blog = await self.get_blog_by_id(blog_like.blog_id)
        if not blog:
            logger.warning(f"Blog not found for liking: {blog_like.blog_id}")
            raise NotFoundException("Blog not found")
        
        like = await self.create(blog_like)
        blog.like_count += 1
        await self.update(blog)
        
        return like
    
    async def unlike_blog(self, 
                          blog_id: int, 
                          user_id: int) -> None:
        # Fetch the blog and blog like entry
        blog = await self.get_blog_by_id(blog_id=blog_id)
        if not blog:
            logger.warning(f"Blog not found for unliking: {blog_id}")
            raise NotFoundException("Blog not found")
        
        query = select(BlogLike).filter(
            BlogLike.blog_id == blog_id,
            BlogLike.user_id == user_id
        )
        blog_like = await self.get_one(query)
        
        if not blog_like:
            logger.warning(f"Blog like not found for unliking: blog_id={blog_id}, user_id={user_id}")
            raise NotFoundException("Blog like not found")
        
        await self.delete(blog_like)
        blog.like_count = max(blog.like_count - 1, 0)
        await self.update(blog)
        
    async def bookmark_blog(self, 
                            blog_bookmark: BlogBookmark) -> BlogBookmark:
        # Fetch the blog
        blog = await self.get_blog_by_id(blog_bookmark.blog_id)
        if not blog:
            logger.warning(f"Blog not found for bookmarking: {blog_bookmark.blog_id}")
            raise NotFoundException("Blog not found")
        
        bookmark = await self.create(blog_bookmark)
        blog.bookmark_count += 1
        await self.update(blog)
        
        return bookmark
        
    async def unbookmark_blog(self, 
                              blog_id: int, 
                              user_id: int) -> None:
        # Fetch the blog and blog bookmark entry
        blog = await self.get_blog_by_id(blog_id=blog_id)
        if not blog:
            logger.warning(f"Blog not found for unbookmarking: {blog_id}")
            raise NotFoundException("Blog not found")
        
        query = select(BlogBookmark).filter(
            BlogBookmark.blog_id == blog_id,
            BlogBookmark.user_id == user_id
        )
        blog_bookmark = await self.get_one(query)
        
        if not blog_bookmark:
            logger.warning(f"Blog Bookmark not found for unbookmarking: blog_id={blog_id}, user_id={user_id}")
            raise NotFoundException("Blog bookmark not found")
        
        await self.delete(blog_bookmark)
        blog.bookmark_count = max(blog.bookmark_count - 1, 0)
        await self.update(blog)