import logging
import uuid

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import (
    UserBase, UserCreate, UserResponse, UserCreateResponse,
    UserUpdateResponse
)
from .service import UserService
from .dependency import get_user_service

from app.core.schemas import StandardResponse
from app.core.response import success_response
from app.core.security import get_current_admin_user, get_current_user
from app.core.exception import PermissionDeniedException
from app.services.task_service import get_task_status, TaskStatusResponse

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.post("/create-user", response_model=StandardResponse[UserCreateResponse])
async def create_user(request: UserCreate, 
                      user_service: UserService = Depends(get_user_service)):
    logger.info(f"User creation requested for email: {request.email}")
    response = await user_service.create_user(request) 
    return success_response("User created successfully", response)

@router.get("/admin/get-user/all", response_model=StandardResponse[list[UserResponse]])
async def get_all_users(user_service: UserService = Depends(get_user_service),
                        admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching all users")
    response = await user_service.get_all_users()
    return success_response("All users fetched successfully", response)

@router.get("/get-user/{user_id}", response_model=StandardResponse[UserResponse])
async def get_user(user_id: uuid.UUID = None, 
                   user_service: UserService = Depends(get_user_service),
                   current_user: User = Depends(get_current_user)):
    if user_id and current_user.is_admin:
        logger.info(f"Admin {current_user.email} is fetching user details for user_id: {user_id}")
        response = await user_service.get_user_by_id(user_id)
        return success_response("User fetched successfully", response)
    
    elif user_id and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted to access user details for user_id: {user_id}")
        raise PermissionDeniedException("Only admins can access other users' details")
    
    logger.info(f"User {current_user.email} is fetching user details for user_id: {user_id}")
    return success_response("User fetched successfully", response)

@router.put("/admin/update-user/{user_id}", response_model=StandardResponse[UserUpdateResponse])
async def update_user(user_id: uuid.UUID,
                      request: UserBase,
                      user_service: UserService = Depends(get_user_service),
                      admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is updating user details for user_id: {user_id}")
    response = await user_service.update_user(user_id, request)
    return success_response("User updated successfully", response)

@router.put("/update-user", response_model=StandardResponse[UserUpdateResponse])
async def update_current_user(request: UserBase,
                              user_service: UserService = Depends(get_user_service),
                              current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating their own details")
    response = await user_service.update_current_user(current_user, request)
    return success_response("User updated successfully", response)

@router.delete("/delete-user")
async def delete_user(user_service: UserService = Depends(get_user_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting their own account")
    response = await user_service.delete_user(current_user)
    return success_response("User deleted successfully", response)

@router.delete("/admin/delete-user/{user_id}")
async def delete_specific_user(user_id: uuid.UUID,
                               user_service: UserService = Depends(get_user_service),
                               admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is deleting user with user_id: {user_id}")
    response = await user_service.delete_specific_user(user_id)
    return success_response("User deleted successfully", response)


#----------------------------
# Task Status Tracking
#----------------------------

@router.get("/task/status/{task_id}", response_model=TaskStatusResponse)
async def get_user_task_status(task_id: str = Path(..., description="The task ID to check status for")):
    """Get the status of a user task (e.g., welcome email) by task ID."""
    logger.info(f"Checking task status for: {task_id}")
    return get_task_status(task_id)
