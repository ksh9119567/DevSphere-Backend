import logging
from typing import Union
import uuid

from .models import Blog
from .schemas import BlogBase

from app.core.exception import NotFoundException
from app.core.repositories.user_repository import UserRepository
from app.core.repositories.cached_blog_repository import CachedBlogRepository
from app.services.base_service import BaseService
from app.events import event_dispatcher
from app.events.events.blog_events import (
    BlogCreatedEvent, BlogUpdatedEvent, BlogDeletedEvent, AllBlogDeletedEvent,
)

logger = logging.getLogger(__name__)


class BlogService(BaseService):
    """
    Blog service with event-driven cache invalidation.
    
    Responsibilities:
    - Business logic for blog operations
    - User authorization checks
    - Event dispatching for cache invalidation
    - Error handling and validation
    """

    def __init__(self, cached_blog_repo: CachedBlogRepository, user_repo: UserRepository):
        """
        Initialize BlogService with cached repository.
        
        Args:
            cached_blog_repo: CachedBlogRepository instance (injected)
            user_repo: UserRepository instance (injected)
        """
        self.blog_repo = cached_blog_repo
        self.user_repo = user_repo

    async def create_blog(self, request: BlogBase, user_id: Union[str, uuid.UUID]) -> Blog:
        """
        Create a new blog and dispatch creation event.
        
        Event: BlogCreatedEvent → triggers cache invalidation
        """
        logger.info(f"Creating blog '{request.title}' for user_id={user_id}")

        new_blog = Blog(
            title=request.title,
            content=request.content,
            user_id=user_id
        )

        blog = await self.blog_repo.create_blog(new_blog)
        
        # Dispatch event for cache invalidation
        dispatch_result = await event_dispatcher.dispatch(
            BlogCreatedEvent(blog_id=blog.id, user_id=user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
        
        logger.info(f"Blog created with id={blog.id}")
        return {"blog": blog, "task_id": task_id}

    async def get_user_blogs(self, user_id: Union[str, uuid.UUID]) -> list[Blog]:
        """
        Get all blogs for a user (cached).
        
        Cache: user:{user_id}:blogs (5 min TTL)
        """
        logger.debug(f"Fetching blogs for user_id={user_id}")
        
        user = await self.user_repo.get_user_by_id(user_id)
        await self.get_or_404(user, "User")

        blogs = await self.blog_repo.get_user_blogs(user_id)

        if not blogs:
            raise NotFoundException("Blogs")

        return blogs

    async def get_all_blogs(self) -> list[Blog]:
        """
        Get all blogs (admin view, cached).
        
        Cache: blog:list:all (5 min TTL)
        """
        logger.debug("Fetching all blogs")
        
        blogs = await self.blog_repo.get_all_blogs()

        if not blogs:
            raise NotFoundException("Blogs")

        return blogs

    async def get_blog(self, blog_id: Union[str, uuid.UUID], user_id: Union[str, uuid.UUID]) -> Blog:
        """
        Get a specific blog by ID (cached).
        
        Cache: blog:{blog_id} (10 min TTL)
        """
        logger.debug(f"Fetching blog_id={blog_id} for user_id={user_id}")
        
        blog = await self.blog_repo.get_user_blog_by_id(blog_id, user_id)
        await self.get_or_404(blog, "Blog")
        
        return blog

    async def update_blog(
        self, 
        blog_id: Union[str, uuid.UUID], 
        request: BlogBase, 
        user_id: Union[str, uuid.UUID], 
        is_admin: bool
    ) -> Blog:
        """
        Update a blog and dispatch update event.
        
        Event: BlogUpdatedEvent → triggers cache invalidation
        """
        logger.info(f"Updating blog_id={blog_id} by user_id={user_id}")
        
        if is_admin:
            # Use get_blog_by_id_for_update to bypass cache and get fresh ORM object
            blog = await self.blog_repo.get_blog_by_id_for_update(blog_id)
        else:
            blog = await self.blog_repo.get_user_blog_by_id(blog_id, user_id)

        blog = await self.get_or_404(blog, "Blog")

        blog.title = request.title or blog.title
        blog.content = request.content or blog.content

        updated_blog = await self.blog_repo.update_blog(blog)
        
        # Dispatch event for cache invalidation
        dispatch_result = await event_dispatcher.dispatch(
            BlogUpdatedEvent(blog_id=blog_id, user_id=blog.user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
        
        logger.info(f"Blog updated: {blog_id}")
        return {"blog": updated_blog, "task_id": task_id}

    async def delete_blog(
        self, 
        blog_id: Union[str, uuid.UUID], 
        user_id: Union[str, uuid.UUID], 
        is_admin: bool
    ) -> str:
        """
        Delete a blog and dispatch deletion event.
        
        Event: BlogDeletedEvent → triggers cache invalidation
        """
        logger.info(f"Deleting blog_id={blog_id} by user_id={user_id}")
        
        if is_admin:
            # Use get_blog_by_id_for_update to bypass cache and get fresh ORM object
            blog = await self.blog_repo.get_blog_by_id_for_update(blog_id)
        else:
            blog = await self.blog_repo.get_user_blog_by_id(blog_id, user_id)

        blog = await self.get_or_404(blog, "Blog")

        await self.blog_repo.delete_blog(blog)
        
        # Dispatch event for cache invalidation
        dispatch_result = await event_dispatcher.dispatch(
            BlogDeletedEvent(blog_id=blog_id, user_id=blog.user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
        
        logger.info(f"Blog deleted: {blog_id}")
        return {"task_id": task_id}
    
    async def delete_all_blogs(self, user_id: Union[str, uuid.UUID]):
        await self.blog_repo.delete_all_blogs(user_id)
        dispatch_result = await event_dispatcher.dispatch(
            AllBlogDeletedEvent(blog_id=None, user_id=user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
            
        logger.info(f"All blogs deleted for user_id={user_id}")
        return {"task_id": task_id}