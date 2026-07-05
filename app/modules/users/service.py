import logging
import uuid

from datetime import datetime, timezone
from typing import Union
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import bcrypt

from .models import User, UserFollow
from .schemas import UserCreate, UserBase
from .repositories.cached_user_repository import CachedUserRepository

from app.core.exception import ValidationException
from app.services.base_service import BaseService
from app.events import event_dispatcher
from app.events.events.user_events import (
    UserRegisteredEvent, UserUpdatedEvent, UserDeletedEvent, UserFollowEvent,
    UserUnFollowEvent
)

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """
    User service with event-driven cache invalidation.
    
    Responsibilities:
    - Business logic for user operations
    - User validation and authorization
    - Event dispatching for cache invalidation
    - Error handling
    """

    def __init__(self, cached_user_repo: CachedUserRepository):
        """
        Initialize UserService with cached repository.
        
        Args:
            cached_user_repo: CachedUserRepository instance (injected)
        """
        self.user_repo = cached_user_repo

    async def create_user(self, request: UserCreate) -> dict:
        """
        Create a new user and dispatch registration event.
        
        Event: UserRegisteredEvent → triggers cache invalidation
        """
        logger.info(f"Creating user with email: {request.email}")

        hashed_pwd = bcrypt.hash(request.password)

        new_user = User(
            username=request.username,
            email=request.email,
            password=hashed_pwd,
            display_name=request.display_name if request.display_name else request.username,
            profile_image=request.profile_image,
            profile_bio=request.profile_bio,
            headline=request.headline,
            location=request.location,
            website=request.website,
            linkedin=request.linkedin,
            github=request.github,
            last_login=datetime.now(timezone.utc),
            is_email_verified=request.is_email_verified or False
        )

        try:
            user = await self.user_repo.create_user(new_user)

            # Dispatch event for cache invalidation and email notification
            dispatch_result = await event_dispatcher.dispatch(
                UserRegisteredEvent(email=request.email, user_id=user.id)
            )
            task_id = None
            if dispatch_result and len(dispatch_result) > 0:
                task_id = dispatch_result[0].get("task_id")
            
            logger.info(f"User created with id={user.id}")
            return {"user": user, "task_id": task_id}
        
        except SQLAlchemyError as e:
            logger.warning(f"Database error creating user: {request.email} - {str(e)}")
            raise ValidationException(e)

    async def get_all_users(self) -> list[User]:
        """
        Get all users (cached).
        
        Cache: user:list:all (5 min TTL)
        """
        logger.debug("Fetching all users")

        users = await self.user_repo.get_all_users()

        if not users:
            raise ValidationException("No users found")

        return users

    async def get_user_by_id(self, user_id: Union[str, uuid.UUID], is_admin: bool) -> User:
        """
        Get a specific user by ID (cached).
        
        Cache: user:{user_id} (10 min TTL)
        """
        logger.debug(f"Fetching user_id={user_id}")
        
        user = await self.user_repo.get_user_by_id(user_id, is_admin)
        await self.get_or_404(user, "User")
        
        return user

    async def update_user(self, user_id: Union[str, uuid.UUID], request: UserBase, is_admin: bool) -> User:
        """
        Update a user and dispatch update event.
        
        Event: UserUpdatedEvent → triggers cache invalidation
        """
        logger.info(f"Updating user: {user_id}")

        # Use get_user_by_id_for_update to bypass cache and get fresh ORM object
        user = await self.user_repo.get_user_by_id_for_update(user_id, is_admin)
        user = await self.get_or_404(user, "User")

        user.display_name = request.display_name or user.display_name
        user.profile_image = request.profile_image or user.profile_image
        user.profile_bio = request.profile_bio or user.profile_bio
        user.headline = request.headline or user.headline
        user.location = request.location or user.location
        user.website = request.website or user.website
        user.linkedin = request.linkedin or user.linkedin
        user.github = request.github or user.github
        user.is_private_account = request.is_private_account or user.is_private_account
        
        if is_admin:
            user.is_admin = request.is_admin or user.is_admin
            user.is_active = request.is_active or user.is_active
            user.is_deleted = request.is_deleted or user.is_deleted
            user.is_verified = request.is_verified or user.is_verified
            user.is_suspended = request.is_suspended or user.is_suspended

        try:
            updated_user = await self.user_repo.update_user(user)
            
            # Dispatch event for cache invalidation
            dispatch_result = await event_dispatcher.dispatch(
                UserUpdatedEvent(user_id=user_id, email=user.email)
            )
            task_id = None
            if dispatch_result and len(dispatch_result) > 0:
                task_id = dispatch_result[0].get("task_id")
            
            logger.info(f"User updated: {user_id}")
            return {"user": updated_user, "task_id": task_id}

        except SQLAlchemyError as e:
            logger.warning(f"Database error updating user {user_id}: {str(e)}")
            raise ValidationException("Email already in use")

    async def update_current_user(self, current_user: User, request: UserBase) -> User:
        """
        Update current user profile and dispatch update event.
        
        Event: UserUpdatedEvent → triggers cache invalidation
        """
        logger.info(f"{current_user.email} updating own profile")

        current_user.username = request.username or current_user.username
        current_user.display_name = request.display_name or current_user.display_name
        current_user.profile_image = request.profile_image or current_user.profile_image
        current_user.profile_bio = request.profile_bio or current_user.profile_bio
        current_user.headline = request.headline or current_user.headline
        current_user.location = request.location or current_user.location
        current_user.website = request.website or current_user.website
        current_user.linkedin = request.linkedin or current_user.linkedin
        current_user.github = request.github or current_user.github
        current_user.is_private_account = request.is_private_account or current_user.is_private_account

        try:
            updated_user = await self.user_repo.update_user(current_user)
            
            # Dispatch event for cache invalidation
            dispatch_result = await event_dispatcher.dispatch(
                UserUpdatedEvent(user_id=current_user.id, email=current_user.email)
            )
            task_id = None
            if dispatch_result and len(dispatch_result) > 0:
                task_id = dispatch_result[0].get("task_id")
            
            logger.info(f"User profile updated: {current_user.id}")
            return {"user": updated_user, "task_id": task_id}

        except SQLAlchemyError as e:
            logger.warning(f"Database error updating profile for {current_user.email}: {str(e)}")
            raise ValidationException("Email already in use")

    async def delete_current_user(self, current_user: User) -> str:
        """
        Delete current user and dispatch deletion event.
        
        Event: UserDeletedEvent → triggers cache invalidation
        """
        logger.info(f"{current_user.email} deleting own account")

        if current_user.is_admin:
            is_last_admin = await self.user_repo.is_last_admin()

            if is_last_admin:
                raise ValidationException("Cannot delete the last admin user")

        await self.user_repo.delete_user(current_user)
        
        # Dispatch event for cache invalidation
        dispatch_result = await event_dispatcher.dispatch(
            UserDeletedEvent(user_id=current_user.id, email=current_user.email)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
            
        logger.info(f"User deleted: {current_user.id}")
        return {"task_id": task_id}

    async def delete_specific_user(self, user_id: Union[str, uuid.UUID], is_admin: bool) -> str:
        """
        Delete specific user and dispatch deletion event.
        
        Event: UserDeletedEvent → triggers cache invalidation
        """
        logger.info(f"Deleting user: {user_id}")

        # Use get_user_by_id_for_update to bypass cache and get fresh ORM object
        user = await self.user_repo.get_user_by_id_for_update(user_id, is_admin)
        user = await self.get_or_404(user, "User")

        if user.is_admin:
            raise ValidationException("Cannot delete admin users")

        await self.user_repo.delete_user(user)
        
        # Dispatch event for cache invalidation
        dispatch_result = await event_dispatcher.dispatch(
            UserDeletedEvent(user_id=user_id, email=user.email)
        )
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
            
        logger.info(f"User deleted: {user_id}")
        return {"task_id": task_id}
    
    async def follow_user(self, follower_id: Union[str, uuid.UUID], following_id: Union[str, uuid.UUID]) -> str:
        """
        Follow a user and dispatch follow event.
        
        Event: UserFollowEvent → triggers cache invalidation
        """
        logger.info(f"User {follower_id} is following user {following_id}")
        
        if follower_id == following_id:
            logger.warning(f"User {follower_id} attempted to follow themselves")
            raise ValidationException("Users cannot follow themselves")
        
        new_follow = UserFollow(
            follower_id = follower_id,
            following_id = following_id
        )
        
        try:
            follow = await self.user_repo.follow_user(new_follow)
            
            dispatch_result = await event_dispatcher.dispatch(
                UserFollowEvent(follower_id=follower_id, following_id=following_id)
            )
            
            task_id = None
            if dispatch_result and len(dispatch_result) > 0:
                task_id = dispatch_result[0].get("task_id")
            
            logger.info(f"User {follower_id} followed user {following_id}")
            return {"task_id": task_id}
        
        except SQLAlchemyError as e:
            logger.warning(f"Database error following user: {follower_id} -> {following_id} - {str(e)}")
            raise ValidationException("Already following this user")
        
    async def unfollow_user(self, follower_id: Union[str, uuid.UUID], following_id: Union[str, uuid.UUID]) -> str:
        """
        Unfollow a user and dispatch unfollow event.
        
        Event: UserUnFollowEvent → triggers cache invalidation
        """
        logger.info(f"User {follower_id} is unfollowing user {following_id}")
        
        try:
            await self.user_repo.unfollow_user(follower_id, following_id)
            dispatch_result = await event_dispatcher.dispatch(
                UserUnFollowEvent(follower_id=follower_id, following_id=following_id)
            )
            
            task_id = None
            if dispatch_result and len(dispatch_result) > 0:
                task_id = dispatch_result[0].get("task_id")
                
            logger.info(f"User {follower_id} unfollowed user {following_id}")
            return {"task_id": task_id}
        
        except SQLAlchemyError as e:
            logger.warning(f"Database error unfollowing user: {follower_id} -> {following_id} - {str(e)}")
            raise ValidationException("Not following this user")
        
    async def get_followers(self, user_id: Union[str, uuid.UUID]) -> list[User]:
        """
        Get followers for a user
        """
        logger.info(f"Fetching followers for user {user_id}")
        followers = await self.user_repo.get_followers(user_id)
        return followers
    
    async def get_following(self, user_id: Union[str, uuid.UUID]) -> list[User]:
        """
        Get users that a user is following
        """
        logger.info(f"Fetching following for user {user_id}")
        following = await self.user_repo.get_following(user_id)
        return following