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
)

logger = logging.getLogger(__name__)

cache = CacheManager(redis_client)


async def invalidate_user_cache(event: Union[UserRegisteredEvent, UserUpdatedEvent, UserDeletedEvent]):
    """
    Invalidate user-related caches when user events occur.
    
    Strategy:
    - Delete the specific user cache (user:{user_id})
    - Delete user email cache (user:email:{email})
    - Delete all user list caches (user:list:*)
    
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
    
    # Delete all user list caches
    await cache.delete_pattern(CacheKeys.user_list_pattern())
    
    logger.debug(f"Cache invalidation completed for {event_type}")
