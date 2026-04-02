from app.events.registry import EventRegistry
from app.events.dispatcher import EventDispatcher

from app.events.events.user_events import (
    EmailOTPRequestedEvent,
    UserRegisteredEvent,
    UserUpdatedEvent,
    UserDeletedEvent,
)
from app.events.events.blog_events import BlogCreatedEvent, BlogUpdatedEvent, BlogDeletedEvent, AllBlogDeletedEvent

from app.events.handlers.email_handler import handle_email_otp
from app.events.handlers.user_handler import (
    handle_user_registered, handle_user_updated, handle_user_deleted
)
from app.events.handlers.blog_handler import (
    handle_blog_created, handle_blog_updated, handle_blog_deleted, handle_all_blog_deleted
)
from app.events.handlers.blog_cache_handler import invalidate_blog_cache
from app.events.handlers.user_cache_handler import invalidate_user_cache


registry = EventRegistry()

# Register blog cache invalidation handlers
registry.register(BlogCreatedEvent, handle_blog_created)
registry.register(BlogCreatedEvent, invalidate_blog_cache)
registry.register(BlogUpdatedEvent, handle_blog_updated)
registry.register(BlogUpdatedEvent, invalidate_blog_cache)
registry.register(BlogDeletedEvent, handle_blog_deleted)
registry.register(BlogDeletedEvent, invalidate_blog_cache)
registry.register(AllBlogDeletedEvent, handle_all_blog_deleted)
registry.register(AllBlogDeletedEvent, invalidate_blog_cache)

# Register user cache invalidation handlers
registry.register(UserRegisteredEvent, handle_user_registered)
registry.register(UserRegisteredEvent, invalidate_user_cache)
registry.register(UserUpdatedEvent, handle_user_updated)
registry.register(UserUpdatedEvent, invalidate_user_cache)
registry.register(UserDeletedEvent, handle_user_deleted)
registry.register(UserDeletedEvent, invalidate_user_cache)

# Register email handlers
registry.register(EmailOTPRequestedEvent, handle_email_otp)

# Global dispatcher instance
event_dispatcher = EventDispatcher(registry)