import logging
import uuid

from fastapi import APIRouter, Depends, Path

from .models import User
from .schemas import (
    UserCreate, UserCreateResponse, UserPrivateResponse, UserPublicResponse,
    UserUpdate, UserListResponse
)
from .service import UserService
from .dependency import get_user_service

from app.core.schemas import StandardResponse
from app.core.response import success_response
from app.core.security import get_current_user
from app.services.task_service import get_task_status, TaskStatusResponse

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)

#---------------------------------------
# User Creation and management endpoints
#---------------------------------------
# Both for admin and normal users
@router.post("/create/user", response_model=StandardResponse[UserCreateResponse])
async def create_user(request: UserCreate, 
                      user_service: UserService = Depends(get_user_service)):
    logger.info(f"User creation requested for email: {request.email}")
    response = await user_service.create_user(request) 
    return success_response("User created successfully", response["user"])

@router.get("/get/user/current", response_model=StandardResponse[UserPrivateResponse])
async def get_current_user(user_service: UserService  = Depends(get_user_service),
                           current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching their own details")
    response = await user_service.get_user_by_id(current_user.id, current_user.is_admin)
    return success_response("User fetched successfully", response)

@router.get("/get/user/{user_id}", response_model=StandardResponse[UserPublicResponse])
async def get_user(user_id: uuid.UUID = None, 
                   user_service: UserService = Depends(get_user_service),
                   current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching user details for user_id: {user_id}")
    response = await user_service.get_user_by_id(user_id, current_user.is_admin)
    return success_response("User fetched successfully", response)

@router.put("/update/user/current", response_model=StandardResponse[UserPrivateResponse])
async def update_current_user(request: UserUpdate,
                              user_service: UserService = Depends(get_user_service),
                              current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating their own details")
    response = await user_service.update_current_user(current_user, request)
    return success_response("User updated successfully", response["user"])

@router.delete("/delete/user")
async def delete_current_user(user_service: UserService = Depends(get_user_service),
                              current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting their own account")
    response = await user_service.delete_current_user(current_user)
    return success_response("User deleted successfully", response)

#-------------------------------------------
# User enagement endpoints (follow/unfollow)
#-------------------------------------------
@router.post("/follow/user/{user_id}")
async def follow_user(user_id: uuid.UUID,
                      user_service: UserService = Depends(get_user_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is following user_id: {user_id}")
    response = await user_service.follow_user(current_user.id, user_id)
    return success_response("User followed successfully", response)

@router.delete("/unfollow/user/{user_id}")
async def unfollow_user(user_id: uuid.UUID,
                        user_service: UserService = Depends(get_user_service),
                        current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is unfollowing user_id: {user_id}")
    response = await user_service.unfollow_user(current_user.id, user_id)
    return success_response("User unfollowed successfully", response)

@router.get("/get/followers/current", response_model=StandardResponse[list[UserListResponse]])
async def get_current_user_followers(user_service: UserService = Depends(get_user_service),
                                     current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching their followers")
    response = await user_service.get_followers(current_user.id)
    return success_response("User followers fetched successfully", response)

@router.get("/get/following/current", response_model=StandardResponse[list[UserListResponse]])
async def get_current_user_following(user_service: UserService = Depends(get_user_service),
                                     current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching their following")
    response = await user_service.get_following(current_user.id)
    return success_response("User following fetched successfully", response)

#---------------------
# Task Status Tracking
#---------------------
@router.get("/task/status/{task_id}", response_model=TaskStatusResponse)
async def get_user_task_status(task_id: str = Path(..., description="The task ID to check status for")):
    """Get the status of a user task (e.g., welcome email) by task ID."""
    logger.info(f"Checking task status for: {task_id}")
    return get_task_status(task_id)
