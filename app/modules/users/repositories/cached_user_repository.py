import logging
import uuid

from typing import Optional, Union

from .user_repository import UserRepository
from app.core.cache_manager import CacheManager
from app.core.cache_keys import CacheKeys
from app.core.cache_config import cache_ttl
from app.modules.users.models import User, UserFollow

logger = logging.getLogger(__name__)


class CachedUserRepository:
    """
    Decorator pattern for UserRepository that adds Redis caching layer.
    
    Architecture:
    - Read operations: Try cache first, fallback to DB, store in cache
    - Write operations: Always go to DB, invalidate related caches
    """

    def __init__(self, user_repo: UserRepository, cache: CacheManager):
        self.user_repo = user_repo
        self.cache = cache

    def _user_to_dict(self, user: User) -> dict:
        """Convert User ORM object to dictionary for caching.
        
        Includes profile, analytics, and status fields to provide complete user data when cached.
        """
        if isinstance(user, dict):
            return user
        
        # Serialize blogs if they exist
        blogs = []
        if hasattr(user, 'blogs') and user.blogs:
            blogs = [
                {
                    'id': str(blog.id),
                    'user_id': str(blog.user_id),
                    'title': blog.title,
                    'content': blog.content,
                    'slug': blog.slug,
                    'status': blog.status,
                    'created_at': blog.created_at.isoformat() if blog.created_at else None,
                    'updated_at': blog.updated_at.isoformat() if blog.updated_at else None,
                }
                for blog in user.blogs
            ]
        
        return {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'password': user.password,
            'display_name': user.display_name,
            'profile_image': user.profile_image,
            'profile_bio': user.profile_bio,
            'headline': user.headline,
            'location': user.location,
            'website': user.website,
            'linkedin': user.linkedin,
            'github': user.github,
            'follower_count': user.follower_count,
            'following_count': user.following_count,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_private_account': user.is_private_account,
            'is_admin': user.is_admin,
            'is_email_verified': user.is_email_verified,
            'is_active': user.is_active,
            'is_deleted': user.is_deleted,
            'is_verified': user.is_verified,
            'is_suspended': user.is_suspended,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        }

    async def get_user_by_id(self, user_id: Union[str, uuid.UUID], is_admin: bool) -> Optional[User]:
        """
        Get a single user by ID with caching.
        
        Cache key: user:{user_id}
        TTL: 10 minutes
        
        Returns: Dictionary from cache or User ORM object from DB
        Note: For write operations, use get_user_by_id_for_update() instead
        """
        key = CacheKeys.user(user_id)
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug(f"User {user_id} retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        user = await self.user_repo.get_user_by_id(user_id, is_admin)
        
        # Store in cache if found
        if user:
            user_dict = self._user_to_dict(user)
            await self.cache.set(key, user_dict, cache_ttl.USER_DETAIL)
            logger.debug(f"User {user_id} cached for {cache_ttl.USER_DETAIL}s")
        
        return user

    async def get_user_by_id_for_update(self, user_id: Union[str, uuid.UUID], is_admin: bool) -> Optional[User]:
        """
        Get a single user by ID for update operations (bypasses cache).
        
        Always fetches fresh User ORM object from database.
        Used for write operations (update, delete) that need ORM object attributes.
        
        Returns: User ORM object (never cached)
        """
        logger.debug(f"User {user_id} retrieved from DB for update (cache bypassed)")
        return await self.user_repo.get_user_by_id(user_id, is_admin)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email with caching.
        
        Cache key: user:email:{email}
        TTL: 10 minutes
        
        Returns: Dictionary from cache or User ORM object from DB
        Note: For write operations, use get_user_by_email_for_update() instead
        """
        key = CacheKeys.user_by_email(email)
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug(f"User {email} retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        user = await self.user_repo.get_user_by_email(email)
        
        # Store in cache if found
        if user:
            user_dict = self._user_to_dict(user)
            await self.cache.set(key, user_dict, cache_ttl.USER_DETAIL)
            logger.debug(f"User {email} cached for {cache_ttl.USER_DETAIL}s")
        
        return user

    async def get_user_by_email_for_update(self, email: str) -> Optional[User]:
        """
        Get a user by email for update operations (bypasses cache).
        
        Always fetches fresh User ORM object from database.
        Used for write operations (update, delete) that need ORM object attributes.
        
        Returns: User ORM object (never cached)
        """
        logger.debug(f"User {email} retrieved from DB for update (cache bypassed)")
        return await self.user_repo.get_user_by_email(email)

    async def get_all_users(self) -> list[User]:
        """
        Get all users with caching.
        
        Cache key: user:list:all
        TTL: 5 minutes
        """
        key = CacheKeys.user_list_all()
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug("All users retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        users = await self.user_repo.get_all_users()
        
        # Store in cache
        users_dicts = [self._user_to_dict(user) for user in users]
        await self.cache.set(key, users_dicts, cache_ttl.USER_LIST)
        logger.debug(f"All users cached for {cache_ttl.USER_LIST}s")
        
        return users

    async def get_all_users_except_admins(self) -> list[User]:
        """
        Get all non-admin users with caching.
        
        Cache key: user:list:non-admin
        TTL: 5 minutes
        """
        key = CacheKeys.user_list_non_admin()
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug("Non-admin users retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        users = await self.user_repo.get_all_users_except_admins()
        
        # Store in cache
        users_dicts = [self._user_to_dict(user) for user in users]
        await self.cache.set(key, users_dicts, cache_ttl.USER_LIST)
        logger.debug(f"Non-admin users cached for {cache_ttl.USER_LIST}s")
        
        return users

    # Write operations - always go to DB, no caching
    async def create_user(self, user: User) -> User:
        """Create a user. Write operation - no caching."""
        return await self.user_repo.create_user(user)

    async def update_user(self, user: User) -> User:
        """Update a user. Write operation - no caching."""
        return await self.user_repo.update_user(user)

    async def delete_user(self, user: User) -> None:
        """Delete a user. Write operation - no caching."""
        return await self.user_repo.delete_user(user)

    async def is_last_admin(self) -> bool:
        """Check if this is the last admin. Not cached."""
        return await self.user_repo.is_last_admin()
    
    async def follow_user(self, follow: UserFollow):
        """Follow a user. Write operation - no caching."""
        return await self.user_repo.follow_user(follow)
    
    async def unfollow_user(self, follower_id: Union[str, uuid.UUID], following_id: Union[str, uuid.UUID]):
        """Unfollow a user. Write operation - no caching."""
        return await self.user_repo.unfollow_user(follower_id, following_id)
    
    async def get_followers(self, user_id: Union[str, uuid.UUID]) -> list[User]:
        """
        Get followers of a user with caching.
        
        Cache key: user:{user_id}:followers
        TTL: 5 minutes
        """
        key = CacheKeys.user_followers(user_id)
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug(f"Followers for user {user_id} retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        followers = await self.user_repo.get_followers(user_id)
        
        # Store in cache
        followers_dicts = [self._user_to_dict(user) for user in followers]
        await self.cache.set(key, followers_dicts, cache_ttl.USER_LIST)
        logger.debug(f"Followers for user {user_id} cached for {cache_ttl.USER_LIST}s")
        
        return followers
    
    async def get_following(self, user_id: Union[str, uuid.UUID]) -> list[User]:
        """
        Get users that a user is following with caching.
        
        Cache key: user:{user_id}:following
        TTL: 5 minutes
        """
        key = CacheKeys.user_following(user_id)
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            logger.debug(f"Following for user {user_id} retrieved from cache")
            return cached
        
        # Cache miss - fetch from DB
        following = await self.user_repo.get_following(user_id)
        
        # Store in cache
        following_dicts = [self._user_to_dict(user) for user in following]
        await self.cache.set(key, following_dicts, cache_ttl.USER_LIST)
        logger.debug(f"Following for user {user_id} cached for {cache_ttl.USER_LIST}s")
        
        return following

