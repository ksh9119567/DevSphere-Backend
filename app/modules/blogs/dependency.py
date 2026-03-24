from fastapi import Depends

from .service import BlogService

from app.db.database import get_db
from app.core.cache_manager import CacheManager
from app.core.redis_manager import redis_client
from app.core.repositories.blog_repository import BlogRepository
from app.core.repositories.user_repository import UserRepository
from app.core.repositories.cached_blog_repository import CachedBlogRepository


def get_cache_manager():
    """Provide CacheManager instance."""
    return CacheManager(redis_client)


def get_blog_repository(db=Depends(get_db)):
    """Provide BlogRepository instance."""
    return BlogRepository(db)


def get_user_repository(db=Depends(get_db)):
    """Provide UserRepository instance."""
    return UserRepository(db)


def get_cached_blog_repository(
    blog_repo: BlogRepository = Depends(get_blog_repository),
    cache: CacheManager = Depends(get_cache_manager),
):
    """Provide CachedBlogRepository instance (wraps BlogRepository with caching)."""
    return CachedBlogRepository(blog_repo, cache)


def get_blog_service(
    cached_repo: CachedBlogRepository = Depends(get_cached_blog_repository),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Provide BlogService instance with cached repository and user repository."""
    return BlogService(cached_repo, user_repo)