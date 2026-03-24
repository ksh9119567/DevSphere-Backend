from typing import Union
import uuid


class CacheKeys:
    """
    Centralized cache key generation for consistent key patterns.
    All keys follow the format: domain:entity:identifier
    """

    # ==================== BLOG CACHE KEYS ====================
    
    @staticmethod
    def blog(blog_id: Union[str, uuid.UUID]) -> str:
        """Cache key for a single blog by ID. TTL: 10 minutes"""
        return f"blog:{blog_id}"

    @staticmethod
    def user_blogs(user_id: Union[str, uuid.UUID]) -> str:
        """Cache key for all blogs by a specific user. TTL: 5 minutes"""
        return f"user:{user_id}:blogs"

    @staticmethod
    def blog_list_all() -> str:
        """Cache key for all blogs (admin view). TTL: 5 minutes"""
        return "blog:list:all"

    @staticmethod
    def user_blogs_pattern(user_id: Union[str, uuid.UUID]) -> str:
        """Pattern for invalidating all user blog caches"""
        return f"user:{user_id}:blogs*"

    @staticmethod
    def blog_list_pattern() -> str:
        """Pattern for invalidating all blog list caches"""
        return "blog:list:*"

    # ==================== USER CACHE KEYS ====================
    
    @staticmethod
    def user(user_id: Union[str, uuid.UUID]) -> str:
        """Cache key for a single user by ID. TTL: 10 minutes"""
        return f"user:{user_id}"

    @staticmethod
    def user_by_email(email: str) -> str:
        """Cache key for a user by email. TTL: 10 minutes"""
        return f"user:email:{email}"

    @staticmethod
    def user_list_all() -> str:
        """Cache key for all users. TTL: 5 minutes"""
        return "user:list:all"

    @staticmethod
    def user_list_non_admin() -> str:
        """Cache key for all non-admin users. TTL: 5 minutes"""
        return "user:list:non-admin"

    @staticmethod
    def user_list_pattern() -> str:
        """Pattern for invalidating all user list caches"""
        return "user:list:*"

    @staticmethod
    def user_by_email_pattern() -> str:
        """Pattern for invalidating user email caches"""
        return "user:email:*"