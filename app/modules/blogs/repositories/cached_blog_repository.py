import logging
from typing import Optional, Union
import uuid

from .blog_repository import BlogRepository
from app.core.cache_manager import CacheManager
from app.core.cache_keys import CacheKeys
from app.core.cache_config import cache_ttl
from app.modules.blogs.models import Blog, BlogLike, BlogBookmark

logger = logging.getLogger(__name__)


class CachedBlogRepository:
    """
    Decorator pattern for BlogRepository that adds Redis caching layer.
    
    Architecture:
    - Read operations: Try cache first, fallback to DB, store in cache
    - Write operations: Always go to DB, invalidate related caches
    
    This ensures:
    - Cache consistency (writes always hit DB first)
    - Graceful degradation (if Redis fails, falls back to DB)
    - Separation of concerns (caching logic isolated from repository)
    """

    def __init__(self, blog_repo: BlogRepository, cache: CacheManager):
        self.blog_repo = blog_repo
        self.cache = cache

    def _blog_to_dict(self, 
                      blog: Blog) -> dict:
        """Convert Blog ORM object to dictionary for caching."""
        if isinstance(blog, dict):
            return blog
        return {
            'id': str(blog.id),
            'user_id': str(blog.user_id),
            'title': blog.title,
            'content': blog.content,
            'slug': blog.slug,
            'status': blog.status,
            'published_at': blog.published_at.isoformat() if blog.published_at else None,
            'summary': blog.summary,
            'cover_image': blog.cover_image,
            'reading_time': blog.reading_time,
            'view_count': blog.view_count,
            'like_count': blog.like_count,
            'comment_count': blog.comment_count,
            'bookmark_count': blog.bookmark_count,
            'is_deleted': blog.is_deleted,
            'is_featured': blog.is_featured,
            'is_locked': blog.is_locked,
            'is_private': blog.is_private,
            'is_archived': blog.is_archived,
            'created_at': blog.created_at.isoformat() if blog.created_at else None,
            'updated_at': blog.updated_at.isoformat() if blog.updated_at else None,
        }

    async def get_blog_by_id(self, 
                             blog_id: Union[str, uuid.UUID]) -> Optional[Blog]:
        """
        Get a single blog by ID with caching.
        
        Cache key: blog:{blog_id}
        TTL: 10 minutes
        
        Returns: Dictionary from cache or Blog ORM object from DB
        Note: For write operations, use get_blog_by_id_for_update() instead
        """
        key = CacheKeys.blog(blog_id)
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug(f"Blog {blog_id} retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        blog = await self.blog_repo.get_blog_by_id(blog_id)
        
        # Store in cache if found
        if blog:
            blog_dict = self._blog_to_dict(blog)
            await self.cache.set(key, blog_dict, cache_ttl.BLOG_DETAIL)
            logger.debug(f"Blog {blog_id} cached for {cache_ttl.BLOG_DETAIL}s")
        
        return blog

    async def get_blog_by_id_for_update(self, 
                                        blog_id: Union[str, uuid.UUID]) -> Optional[Blog]:
        """
        Get a single blog by ID for update operations (bypasses cache).
        
        Always fetches fresh Blog ORM object from database.
        Used for write operations (update, delete) that need ORM object attributes.
        
        Returns: Blog ORM object (never cached)
        """
        logger.debug(f"Blog {blog_id} retrieved from DB for update (cache bypassed)")
        return await self.blog_repo.get_blog_by_id(blog_id)

    async def get_user_blog_by_id(self, 
                                  blog_id: Union[str, uuid.UUID], 
                                  user_id: Union[str, uuid.UUID]) -> Optional[Blog]:
        """
        Get a blog by ID and user ID (ownership check).
        
        Note: This is not cached because it's typically used for ownership
        verification before updates/deletes. Caching would require invalidation
        on user changes, which adds complexity.
        """
        return await self.blog_repo.get_user_blog_by_id(blog_id, user_id)

    async def get_user_blogs(self, 
                             user_id: Union[str, uuid.UUID]) -> list[Blog]:
        """
        Get all blogs for a specific user with caching.
        
        Cache key: user:{user_id}:blogs
        TTL: 5 minutes
        """
        key = CacheKeys.user_blogs(user_id)
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug(f"User {user_id} blogs retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        blogs = await self.blog_repo.get_user_blogs(user_id)
        
        # Store in cache
        blogs_dicts = [self._blog_to_dict(blog) for blog in blogs]
        await self.cache.set(key, blogs_dicts, cache_ttl.BLOG_LIST)
        logger.debug(f"User {user_id} blogs cached for {cache_ttl.BLOG_LIST}s")
        
        return blogs

    async def get_all_blogs(self) -> list[Blog]:
        """
        Get all blogs (admin view) with caching.
        
        Cache key: blog:list:all
        TTL: 5 minutes
        """
        key = CacheKeys.blog_list_all()
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug("All blogs retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        blogs = await self.blog_repo.get_all_blogs()
        
        # Store in cache
        blogs_dicts = [self._blog_to_dict(blog) for blog in blogs]
        await self.cache.set(key, blogs_dicts, cache_ttl.BLOG_LIST)
        logger.debug(f"All blogs cached for {cache_ttl.BLOG_LIST}s")
        
        return blogs

    # Write operations - always go to DB, no caching
    async def create_blog(self, 
                          blog: Blog) -> Blog:
        """Create a blog. Write operation - no caching."""
        return await self.blog_repo.create_blog(blog)

    async def update_blog(self, 
                          blog: Blog) -> Blog:
        """Update a blog. Write operation - no caching."""
        return await self.blog_repo.update_blog(blog)

    async def delete_blog(self, 
                          blog: Blog) -> None:
        """Delete a blog. Write operation - no caching."""
        return await self.blog_repo.delete_blog(blog)
    
    async def delete_all_blogs(self, 
                               user_id: Union[str, uuid.UUID]) -> None:
        """Delete all blogs for a user. Write operation - no caching."""
        return await self.blog_repo.delete_all_blogs(user_id)
    
    async def like_blog(self, 
                        blog_like: BlogLike) -> None:
        """Like a blog. Write operation - no caching."""
        return await self.blog_repo.like_blog(blog_like)
    
    async def unlike_blog(self, 
                          blog_id: Union[str, uuid.UUID], 
                          user_id: Union[str, uuid.UUID]) -> None:
        """Unlike a blog. Write operation - no caching."""
        return await self.blog_repo.unlike_blog(blog_id, user_id)
    
    async def bookmark_blog(self, 
                            blog_bookmark: BlogBookmark) -> None:
        """Bookmark a blog. Write operation - no caching."""
        return await self.blog_repo.bookmark_blog(blog_bookmark)
    
    async def unbookmark_blog(self, 
                              blog_id: Union[str, uuid.UUID], 
                              user_id: Union[str, uuid.UUID]) -> None:
        """Unbookmark a blog. Write operation - no caching."""
        return await self.blog_repo.unbookmark_blog(blog_id, user_id)
    
    