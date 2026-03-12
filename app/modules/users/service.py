import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from passlib.hash import bcrypt

from .models import User
from .schemas import UserCreate, UserBase

from app.modules.auth.service import AuthService

from app.core.exception import NotFoundException, ValidationException
from app.core.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService():
    @staticmethod
    async def create_user(request: UserCreate, db: AsyncSession) -> dict:
        logger.info(f"Creating user with email: {request.email}")
        hashed_pwd = bcrypt.hash(request.password)
        new_user = User(username=request.username, email=request.email, password=hashed_pwd, 
                        profile_image=request.profile_image, profile_bio=request.profile_bio)
        try:
            response = await UserRepository.create_user(db, new_user)
            tokens = await AuthService.login(request.email, request.password, db)
            return {
                "user": response,
                **tokens
            }
        except IntegrityError:
            await db.rollback()
            logger.warning(f"Attempt to create user with email: {request.email} failed due to email already in use")
            raise ValidationException("Email already in use")
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {str(e)}")
            raise e

    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[User]:
        logger.debug("Fetching all users")
        users = await UserRepository.get_all_users(db)
        if not users:
            logger.warning("No users found in database")
            raise NotFoundException("Users")
        return users

    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
        logger.debug(f"Fetching user by id: {user_id}")
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found: user_id={user_id}")
            raise NotFoundException("User")
        return user
    
    @staticmethod
    async def update_user(user_id: int, request: UserBase, db: AsyncSession) -> User:
        logger.info(f"Updating user: user_id={user_id}")
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found for update: user_id={user_id}")
            raise NotFoundException("User")
        
        user.username = request.username if request.username else user.username
        user.profile_image = request.profile_image if request.profile_image else user.profile_image
        user.profile_bio = request.profile_bio if request.profile_bio else user.profile_bio
        
        try:
            return await UserRepository.update_user(db, user)
        except IntegrityError:
            await db.rollback()
            logger.warning(f"Failed to update user {user_id}: email already in use")
            raise ValidationException("Email already in use")

    @staticmethod
    async def update_current_user(current_user: User, request: UserBase, db: AsyncSession) -> User:
        logger.info(f"User {current_user.email} is updating their own details")
        current_user.username = request.username if request.username else current_user.username
        current_user.profile_image = request.profile_image if request.profile_image else current_user.profile_image
        current_user.profile_bio = request.profile_bio if request.profile_bio else current_user.profile_bio
        
        try:
            return await UserRepository.update_user(db, current_user)
        except IntegrityError:
            await db.rollback()
            logger.warning(f"Failed to update current user {current_user.email}: email already in use")
            raise ValidationException("Email already in use")

    @staticmethod
    async def delete_user(current_user: User, db: AsyncSession) -> str:
        logger.info(f"User {current_user.email} is deleting their own account")
        if current_user.is_admin:
            is_last_admin = await UserRepository.is_last_admin(db)
            if is_last_admin:
                logger.warning(f"Attempt to delete last admin user: {current_user.email}")
                raise ValidationException("Cannot delete the last admin user")
            
        await UserRepository.delete_user(db, current_user)
        return "User deleted successfully"

    @staticmethod
    async def delete_specific_user(user_id: int, db: AsyncSession) -> str:
        logger.info(f"Deleting user: user_id={user_id}")
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found for deletion: user_id={user_id}")
            raise NotFoundException("User")
        
        if user.is_admin:
            logger.warning(f"Attempt to delete admin user: user_id={user_id}")
            raise ValidationException("Cannot delete admin users")
        
        await UserRepository.delete_user(db, user)
        return "User deleted successfully"

