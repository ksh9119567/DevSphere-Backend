"""
Cache configuration and TTL settings.

This module centralizes all cache-related configuration to make it easy
to adjust TTL values and cache behavior across the application.
"""

from dataclasses import dataclass


@dataclass
class CacheTTL:
    """TTL (Time To Live) configuration for different cache types."""
    
    # Blog caching
    BLOG_DETAIL: int = 600  # 10 minutes - Single blog details
    BLOG_LIST: int = 300    # 5 minutes - Blog lists (user blogs, all blogs)
    
    # User caching
    USER_DETAIL: int = 600  # 10 minutes - Single user details
    USER_LIST: int = 300    # 5 minutes - User lists (all users, non-admin users)


# Global cache TTL instance
cache_ttl = CacheTTL()
