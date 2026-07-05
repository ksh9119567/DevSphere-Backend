from fastapi import Depends

from .service import UserService
from .repositories.user_repository import UserRepository
from .repositories.cached_user_repository import CachedUserRepository

from app.db.database import get_db
from app.core.cache_manager import CacheManager
from app.core.redis_manager import redis_client


def get_cache_manager():
    """Provide CacheManager instance."""
    return CacheManager(redis_client)


def get_user_repository(db=Depends(get_db)):
    """Provide UserRepository instance."""
    return UserRepository(db)


def get_cached_user_repository(
    user_repo: UserRepository = Depends(get_user_repository),
    cache: CacheManager = Depends(get_cache_manager),
):
    """Provide CachedUserRepository instance (wraps UserRepository with caching)."""
    return CachedUserRepository(user_repo, cache)


def get_user_service(
    cached_repo: CachedUserRepository = Depends(get_cached_user_repository),
):
    """Provide UserService instance with cached repository."""
    return UserService(cached_repo)