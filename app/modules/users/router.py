import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import UserBase, UserCreate, UserResponse, UserCreateResponse
from .service import UserService

from app.db.database import get_db
from app.core.security import get_current_admin_user, get_current_user
from app.core.exception import PermissionDeniedException

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.post("/create-user", response_model=UserCreateResponse)
async def create_user(request: UserCreate, 
                      db: AsyncSession = Depends(get_db)):
    logger.info(f"User creation requested for email: {request.email}")
    return await UserService.create_user(request, db)

@router.get("/admin/get-user/all", response_model=list[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db), 
                        admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching all users")
    return await UserService.get_all_users(db)

@router.get("/get-user/{user_id}", response_model=UserResponse)
async def get_user(db: AsyncSession = Depends(get_db), 
                   user_id: uuid.UUID = None, 
                   current_user: User = Depends(get_current_user)):
    if user_id and current_user.is_admin:
        logger.info(f"Admin {current_user.email} is fetching user details for user_id: {user_id}")
        return await UserService.get_user_by_id(user_id, db)
    
    elif user_id and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted to access user details for user_id: {user_id}")
        raise PermissionDeniedException("Only admins can access other users' details")
    
    logger.info(f"User {current_user.email} is fetching user details for user_id: {user_id}")
    return current_user

@router.put("/admin/update-user/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID,
                      request: UserBase,
                      db: AsyncSession = Depends(get_db),
                      admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is updating user details for user_id: {user_id}")
    return await UserService.update_user(user_id, request, db)

@router.put("/update-user", response_model=UserResponse)
async def update_current_user(request: UserBase,
                              db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating their own details")
    return await UserService.update_current_user(current_user, request, db)

@router.delete("/delete-user")
async def delete_user(db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting their own account")
    return await UserService.delete_user(current_user, db)

@router.delete("/admin/delete-user/{user_id}")
async def delete_specific_user(user_id: uuid.UUID,
                               db: AsyncSession = Depends(get_db),
                               admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is deleting user with user_id: {user_id}")
    return await UserService.delete_specific_user(user_id, db)

