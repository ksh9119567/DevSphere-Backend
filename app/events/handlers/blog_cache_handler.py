import logging
from typing import Union
import uuid

from app.core.cache_manager import CacheManager
from app.core.redis_manager import redis_client
from app.core.cache_keys import CacheKeys
from app.events.events.blog_events import (
    BlogCreatedEvent,
    BlogUpdatedEvent,
    BlogDeletedEvent,
)

logger = logging.getLogger(__name__)

cache = CacheManager(redis_client)


async def invalidate_blog_cache(event: Union[BlogCreatedEvent, BlogUpdatedEvent, BlogDeletedEvent]):
    """
    Invalidate blog-related caches when blog events occur.
    
    Strategy:
    - Delete the specific blog cache (blog:{blog_id})
    - Delete the user's blog list cache (user:{user_id}:blogs)
    - Delete all blog list caches (blog:list:*)
    
    This ensures consistency across all views while being efficient
    with pattern-based deletion for list caches.
    """
    blog_id = event.blog_id
    user_id = event.user_id
    event_type = event.__class__.__name__
    
    logger.info(f"Invalidating cache for {event_type}: blog_id={blog_id}, user_id={user_id}")
    
    # Delete specific blog cache
    await cache.delete(CacheKeys.blog(blog_id))
    
    # Delete user's blog list cache
    await cache.delete(CacheKeys.user_blogs(user_id))
    
    # Delete all blog list caches (admin view)
    await cache.delete_pattern(CacheKeys.blog_list_pattern())
    
    logger.debug(f"Cache invalidation completed for {event_type}")