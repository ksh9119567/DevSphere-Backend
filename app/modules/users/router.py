import logging
import uuid

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import UserBase, UserCreate, UserResponse, UserCreateResponse
from .service import UserService
from .dependency import get_user_service

from app.core.security import get_current_admin_user, get_current_user
from app.core.exception import PermissionDeniedException
from app.services.task_service import get_task_status, TaskStatusResponse

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


def convert_user_to_dict(user) -> dict:
    """Convert User ORM object or cached dictionary to dictionary for Pydantic serialization.
    
    Handles both:
    - User ORM objects (from database) - serializes blogs relationship
    - Dictionaries (from Redis cache) - returns as-is with cached blogs
    """
    # If already a dictionary (from cache), return as-is
    if isinstance(user, dict):
        return user
    
    # Serialize blogs if they exist in ORM object
    blogs = []
    if hasattr(user, 'blogs') and user.blogs:
        blogs = [
            {
                'id': str(blog.id),
                'user_id': str(blog.user_id),
                'title': blog.title,
                'content': blog.content,
                'created_at': blog.created_at.isoformat() if hasattr(blog.created_at, 'isoformat') else blog.created_at,
                'updated_at': blog.updated_at.isoformat() if hasattr(blog.updated_at, 'isoformat') else blog.updated_at,
            }
            for blog in user.blogs
        ]
    
    # Convert User ORM object to dictionary
    return {
        'id': str(user.id),
        'email': user.email,
        'username': user.username,
        'profile_image': user.profile_image,
        'profile_bio': user.profile_bio,
        'is_admin': user.is_admin,
        'is_email_verified': user.is_email_verified,
        'is_active': user.is_active,
        'blogs': blogs,
        'created_at': user.created_at.isoformat() if hasattr(user.created_at, 'isoformat') else user.created_at,
        'updated_at': user.updated_at.isoformat() if hasattr(user.updated_at, 'isoformat') else user.updated_at,
    }


@router.post("/create-user", response_model=UserCreateResponse)
async def create_user(request: UserCreate, 
                      user_service: UserService = Depends(get_user_service)):
    logger.info(f"User creation requested for email: {request.email}")
    response = await user_service.create_user(request)
    return {"user": response["data"]}

@router.get("/admin/get-user/all", response_model=list[UserResponse])
async def get_all_users(user_service: UserService = Depends(get_user_service),
                        admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching all users")
    response = await user_service.get_all_users()
    return [UserResponse.model_validate(convert_user_to_dict(user)) for user in response["data"]]

@router.get("/get-user/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID = None, 
                   user_service: UserService = Depends(get_user_service),
                   current_user: User = Depends(get_current_user)):
    if user_id and current_user.is_admin:
        logger.info(f"Admin {current_user.email} is fetching user details for user_id: {user_id}")
        response = await user_service.get_user_by_id(user_id)
        return UserResponse.model_validate(convert_user_to_dict(response["data"]))
    
    elif user_id and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted to access user details for user_id: {user_id}")
        raise PermissionDeniedException("Only admins can access other users' details")
    
    logger.info(f"User {current_user.email} is fetching user details for user_id: {user_id}")
    return UserResponse.model_validate(convert_user_to_dict(current_user))

@router.put("/admin/update-user/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID,
                      request: UserBase,
                      user_service: UserService = Depends(get_user_service),
                      admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is updating user details for user_id: {user_id}")
    response = await user_service.update_user(user_id, request)
    return UserResponse.model_validate(convert_user_to_dict(response["data"]))

@router.put("/update-user", response_model=UserResponse)
async def update_current_user(request: UserBase,
                              user_service: UserService = Depends(get_user_service),
                              current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating their own details")
    response = await user_service.update_current_user(current_user, request)
    return UserResponse.model_validate(convert_user_to_dict(response["data"]))

@router.delete("/delete-user")
async def delete_user(user_service: UserService = Depends(get_user_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting their own account")
    return await user_service.delete_user(current_user)

@router.delete("/admin/delete-user/{user_id}")
async def delete_specific_user(user_id: uuid.UUID,
                               user_service: UserService = Depends(get_user_service),
                               admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is deleting user with user_id: {user_id}")
    return await user_service.delete_specific_user(user_id)


#----------------------------
# Task Status Tracking
#----------------------------

@router.get("/task/status/{task_id}", response_model=TaskStatusResponse)
async def get_user_task_status(task_id: str = Path(..., description="The task ID to check status for")):
    """Get the status of a user task (e.g., welcome email) by task ID."""
    logger.info(f"Checking task status for: {task_id}")
    return get_task_status(task_id)
