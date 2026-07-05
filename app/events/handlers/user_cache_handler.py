import logging
from typing import Union
import uuid

from app.core.cache_manager import CacheManager
from app.core.redis_manager import redis_client
from app.core.cache_keys import CacheKeys
from app.events.events.user_events import (
    UserRegisteredEvent,
    UserUpdatedEvent,
    UserDeletedEvent,
    UserFollowEvent,
    UserUnFollowEvent
)

logger = logging.getLogger(__name__)

cache = CacheManager(redis_client)


async def invalidate_user_cache(
    event: Union[UserRegisteredEvent, 
            UserUpdatedEvent, UserDeletedEvent]
    ):
    
    """
    Invalidate user-related caches when user events occur.
    
    Strategy:
    - Delete the specific user cache (user:{user_id})
    - Delete user email cache (user:email:{email})
    - Delete all user list caches (user:list:*)
    - Delete user social caches (followers, following)
    
    This ensures consistency across all views while being efficient
    with pattern-based deletion for list caches.
    """
    user_id = event.user_id
    email = getattr(event, 'email', None)
    event_type = event.__class__.__name__
    
    logger.info(f"Invalidating cache for {event_type}: user_id={user_id}")
    
    # Delete specific user cache
    await cache.delete(CacheKeys.user(user_id))
    
    # Delete user email cache if available
    if email:
        await cache.delete(CacheKeys.user_by_email(email))
    
    # Delete user social caches (followers, following)
    await cache.delete_pattern(CacheKeys.user_social_pattern(user_id))
    
    # Delete all user list caches
    await cache.delete_pattern(CacheKeys.user_list_pattern())
    
    logger.debug(f"Cache invalidation completed for {event_type}")


async def invalidate_user_follow_cache(
    event: Union[UserFollowEvent, UserUnFollowEvent]
    ):
    
    """
    Invalidate user follow-related caches when follow/unfollow events occur.
    
    Strategy:
    - Delete follower's following list cache (user:{follower_id}:following)
    - Delete followed user's followers list cache (user:{following_id}:followers)
    - Delete both users' main caches to refresh follower/following counts
    - Delete all user list caches
    
    This ensures follow counts and lists are updated across all views.
    """
    follower_id = event.follower_id
    following_id = event.following_id
    event_type = event.__class__.__name__
    
    logger.info(f"Invalidating follow cache for {event_type}: follower_id={follower_id}, following_id={following_id}")
    
    # Delete follower's following list cache
    await cache.delete(CacheKeys.user_following(follower_id))
    
    # Delete followed user's followers list cache
    await cache.delete(CacheKeys.user_followers(following_id))
    
    # Delete both users' main caches to refresh counts
    await cache.delete(CacheKeys.user(follower_id))
    await cache.delete(CacheKeys.user(following_id))
    
    # Delete all user list caches
    await cache.delete_pattern(CacheKeys.user_list_pattern())
    
    logger.debug(f"Cache invalidation completed for {event_type}")
