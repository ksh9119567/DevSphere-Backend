import logging
from typing import Union
import uuid

from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import bcrypt

from .models import User
from .schemas import UserCreate, UserBase

from app.core.exception import ValidationException
from app.core.repositories.cached_user_repository import CachedUserRepository
from app.core.response import success_response
from app.services.base_service import BaseService
from app.events import event_dispatcher
from app.events.events.user_events import UserRegisteredEvent, UserUpdatedEvent, UserDeletedEvent

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
            profile_image=request.profile_image,
            profile_bio=request.profile_bio,
            is_email_verified=request.is_email_verified or False
        )

        try:
            response = await self.user_repo.create_user(new_user)

            # Dispatch event for cache invalidation and email notification
            dispatch_result = await event_dispatcher.dispatch(
                UserRegisteredEvent(email=request.email, user_id=response.id)
            )
            task_id = None
            if dispatch_result and len(dispatch_result) > 0:
                task_id = dispatch_result[0].get("task_id")
            
            logger.info(f"User created with id={response.id}")
            return success_response("User created successfully", response, task_id)

        except SQLAlchemyError as e:
            logger.warning(f"Database error creating user: {request.email} - {str(e)}")
            raise ValidationException("Email already in use")

    async def get_all_users(self) -> list[User]:
        """
        Get all users (cached).
        
        Cache: user:list:all (5 min TTL)
        """
        logger.debug("Fetching all users")

        users = await self.user_repo.get_all_users()

        if not users:
            raise ValidationException("No users found")

        return success_response("Users found successfully", users)

    async def get_user_by_id(self, user_id: Union[str, uuid.UUID]) -> User:
        """
        Get a specific user by ID (cached).
        
        Cache: user:{user_id} (10 min TTL)
        """
        logger.debug(f"Fetching user_id={user_id}")
        
        user = await self.user_repo.get_user_by_id(user_id)
        await self.get_or_404(user, "User")
        
        return success_response("User found successfully", user)

    async def update_user(self, user_id: Union[str, uuid.UUID], request: UserBase) -> User:
        """
        Update a user and dispatch update event.
        
        Event: UserUpdatedEvent → triggers cache invalidation
        """
        logger.info(f"Updating user: {user_id}")

        # Use get_user_by_id_for_update to bypass cache and get fresh ORM object
        user = await self.user_repo.get_user_by_id_for_update(user_id)
        user = await self.get_or_404(user, "User")

        user.username = request.username or user.username
        user.profile_image = request.profile_image or user.profile_image
        user.profile_bio = request.profile_bio or user.profile_bio

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
            return success_response("User profile updated successfully", updated_user, task_id)

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
        current_user.profile_image = request.profile_image or current_user.profile_image
        current_user.profile_bio = request.profile_bio or current_user.profile_bio

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
            return success_response("User profile updated successfully", updated_user, task_id)

        except SQLAlchemyError as e:
            logger.warning(f"Database error updating profile for {current_user.email}: {str(e)}")
            raise ValidationException("Email already in use")

    async def delete_user(self, current_user: User) -> str:
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
        return success_response("User deleted successfully", task_id=task_id)

    async def delete_specific_user(self, user_id: Union[str, uuid.UUID]) -> str:
        """
        Delete specific user and dispatch deletion event.
        
        Event: UserDeletedEvent → triggers cache invalidation
        """
        logger.info(f"Deleting user: {user_id}")

        # Use get_user_by_id_for_update to bypass cache and get fresh ORM object
        user = await self.user_repo.get_user_by_id_for_update(user_id)
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
        return success_response("User deleted successfully", task_id=task_id)