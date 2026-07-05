import logging
import uuid

from fastapi import APIRouter, Depends

from app.modules.users.models import User
from app.modules.users.schemas import (
    UserAdminResponse, UserListResponse, UserAdminUpdate
)
from app.modules.users.service import UserService
from app.modules.users.dependency import get_user_service

from app.core.schemas import StandardResponse
from app.core.response import success_response
from app.core.security import get_current_admin_user

router = APIRouter(prefix="/users")
logger = logging.getLogger(__name__)


@router.get("/get/user/all", response_model=StandardResponse[list[UserListResponse]])
async def get_all_users(user_service: UserService = Depends(get_user_service),
                        admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"Admin {admin_user.email} is fetching all users")
    response = await user_service.get_all_users()
    return success_response("All users fetched successfully", response)

@router.get("/get/user/{user_id}", response_model=StandardResponse[UserAdminResponse])
async def get_user(user_id: uuid.UUID = None,
                   user_service: UserService = Depends(get_user_service),
                   admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"Admin {admin_user.email} is fetching user details for user_id: {user_id}")
    response = await user_service.get_user_by_id(user_id, admin_user.is_admin)
    return success_response("User fetched successfully", response)

@router.put("/update/user/{user_id}", response_model=StandardResponse[UserAdminResponse])
async def update_user(user_id: uuid.UUID,
                      request: UserAdminUpdate,
                      user_service: UserService = Depends(get_user_service),
                      admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"Admin {admin_user.email} is updating user details for user_id: {user_id}")
    response = await user_service.update_user(user_id, request, admin_user.is_admin)
    return success_response("User updated successfully", response["user"])

@router.delete("/delete/user/{user_id}")
async def delete_user(user_id: uuid.UUID,
                      user_service: UserService = Depends(get_user_service),
                      admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"Admin {admin_user.email} is deleting user with user_id: {user_id}")
    response = await user_service.delete_specific_user(user_id, admin_user.is_admin)
    return success_response("User deleted successfully", response)