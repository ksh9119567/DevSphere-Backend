import logging
from typing import Union
import uuid

from .models import Blog, BlogLike, BlogBookmark
from .schemas import BlogCreate, BlogUpdate
from .repositories.cached_blog_repository import CachedBlogRepository

from app.core.exception import NotFoundException
from app.core.slug import slugify
from app.modules.users.repositories.user_repository import UserRepository
from app.services.base_service import BaseService
from app.events import event_dispatcher
from app.events.events.blog_events import (
    BlogCreatedEvent, BlogUpdatedEvent, BlogDeletedEvent, AllBlogDeletedEvent,
    BlogLikeEvent, BlogUnLikeEvent, BlogBookmarkEvent, BlogUnBookmarkEvent
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

    async def generate_unique_slug(self, 
                                   title: str, 
                                   user_id):
        base_slug = slugify(title)

        slug = base_slug
        counter = 1

        # Check DB for uniqueness
        while await self.blog_repo.slug_exists(user_id=user_id, slug=slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug
    
    async def create_blog(self, 
                          request: BlogCreate, 
                          user_id: Union[str, uuid.UUID]) -> Blog:
        """
        Create a new blog and dispatch creation event.
        
        Event: BlogCreatedEvent → triggers cache invalidation
        """
        logger.info(f"Creating blog '{request.title}' for user_id={user_id}")
        
        slug = await self.generate_unique_slug(request.title, user_id)
        
        new_blog = Blog(
            user_id=user_id,
            title=request.title,
            content=request.content,
            slug=slug,
            status="draft",
            summary=request.summary,
            cover_image=request.cover_image,
            is_private=request.is_private
        )

        blog = await self.blog_repo.create_blog(new_blog)
        
        logger.info(f"Blog created with id={blog.id}")
        return {"blog": blog}

    async def get_user_blogs(self, 
                             user_id: Union[str, uuid.UUID]) -> list[Blog]:
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

    async def get_blog(self, 
                       blog_id: Union[str, uuid.UUID]) -> Blog:
        """
        Get a specific blog by ID (cached).
        
        Cache: blog:{blog_id} (10 min TTL)
        """
        logger.debug(f"Fetching blog_id={blog_id}")
        
        blog = await self.blog_repo.get_blog_by_id(blog_id)
        await self.get_or_404(blog, "Blog")
        
        return blog

    async def update_blog(self, 
                          blog_id: Union[str, uuid.UUID], 
                          request: BlogUpdate, 
                          user_id: Union[str, uuid.UUID], 
                          is_admin: bool) -> Blog:
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
        blog.summary = request.summary or blog.summary
        blog.cover_image = request.cover_image or blog.cover_image
        blog.is_private = request.is_private or blog.is_private
        blog.is_locked = request.is_locked or blog.is_locked
        blog.is_archived = request.is_archived or blog.is_archived
        
        if is_admin:
            blog.is_deleted = request.is_deleted or blog.is_deleted
            blog.is_featured = request.is_featured or blog.is_featured

        updated_blog = await self.blog_repo.update_blog(blog)
        
        logger.info(f"Blog updated: {blog_id}")
        return {"blog": updated_blog}

    async def delete_blog(self, 
                          blog_id: Union[str, uuid.UUID], 
                          user_id: Union[str, uuid.UUID], 
                          is_admin: bool) -> str:
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
    
    async def delete_all_blogs(self, 
                               user_id: Union[str, uuid.UUID]):
        """
        Delete all blogs for a user and dispatch deletion event.
        
        Event: AllBlogDeletedEvent → triggers cache invalidation
        """
        logger.info(f"Deleting all blogs for user_id={user_id}")
        
        await self.blog_repo.delete_all_blogs(user_id)
            
        logger.info(f"All blogs deleted for user_id={user_id}")
        return 
    
    async def like_blog(self, 
                        blog_id: Union[str, uuid.UUID], 
                        user_id: Union[str, uuid.UUID]):
        """
        Like a blog and dispatch like event.
        
        Event: BlogLikeEvent → triggers cache invalidation
        """
        logger.info(f"User {user_id} is liking blog {blog_id}")
        
        new_blog_like = BlogLike(
            user_id = user_id,
            blog_id = blog_id
        )
        
        blog_like = await self.blog_repo.like_blog(new_blog_like)
        dispatch_result = await event_dispatcher.dispatch(
            BlogLikeEvent(blog_id=blog_id, user_id=user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
        
        logger.info(f"Blog liked successfully: blog_id={blog_like.blog_id}, user_id={blog_like.user_id}")
        return {"blog_like": blog_like, "task_id": task_id}
    
    async def unlike_blog(self, 
                          blog_id: Union[str, uuid.UUID], 
                          user_id: Union[str, uuid.UUID]):
        """
        Unlike a blog and dispatch unlike event.
        
        Event: BlogUnLikeEvent → triggers cache invalidation
        """
        logger.info(f"User {user_id} is unliking blog {blog_id}")
        await self.blog_repo.unlike_blog(blog_id, user_id)
        dispatch_result = await event_dispatcher.dispatch(
            BlogUnLikeEvent(blog_id=blog_id, user_id=user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
        
        logger.info(f"Blog unliked successfully: blog_id={blog_id}, user_id={user_id}")
        return {"task_id": task_id}
    
    async def bookmark_blog(self, 
                            blog_id: Union[str, uuid.UUID], 
                            user_id: Union[str, uuid.UUID]):
        """
        Bookmark a blog and dispatch bookmark event.
        
        Event: BlogBookmarkEvent → triggers cache invalidation
        """
        logger.info(f"User {user_id} is bookmarking blog {blog_id}")
        
        new_blog_bookmark = BlogBookmark(
            user_id = user_id,
            blog_id = blog_id
        )
        
        blog_bookmark = await self.blog_repo.bookmark_blog(new_blog_bookmark)
        dispatch_result = await event_dispatcher.dispatch(
            BlogBookmarkEvent(blog_id=blog_id, user_id=user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
            
        logger.info(f"Blog bookmarked successfully: blog_id={blog_id}, user_id={user_id}")
        return {"blog_bookmark": blog_bookmark, "task_id": task_id}
    
    async def unbookmark_blog(self, 
                              blog_id: Union[str, uuid.UUID], 
                              user_id: Union[str, uuid.UUID]):
        """
        Unbookmark a blog and dispatch unbookmark event.
        
        Event: BlogUnBookmarkEvent → triggers cache invalidation
        """
        logger.info(f"User {user_id} is unbookmarking blog {blog_id}")
        await self.blog_repo.unbookmark_blog(blog_id, user_id)
        dispatch_result = await event_dispatcher.dispatch(
            BlogUnBookmarkEvent(blog_id=blog_id, user_id=user_id)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
            
        logger.info(f"Blog unbookmarked successfully: blog_id={blog_id}, user_id={user_id}")
        return {"task_id": task_id}