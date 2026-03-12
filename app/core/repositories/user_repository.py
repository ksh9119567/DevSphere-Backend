import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.modules.users.models import User

logger = logging.getLogger(__name__)

class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, user: User) -> User:
        logger.debug(f"Creating user: {user.email}")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User created successfully with email: {user.email}")
        return user

    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[User]:
        logger.debug("Fetching all users")
        result = await db.execute(select(User).filter(User.is_active == True, User.is_deleted == False))
        return result.scalars().all()

    @staticmethod
    async def get_all_users_except_admins(db: AsyncSession) -> list[User]:
        logger.debug("Fetching all non-admin users")
        result = await db.execute(select(User).filter(User.is_admin == False, User.is_deleted == False))
        return result.scalars().all()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        logger.debug(f"Fetching user by id: {user_id}")
        result = await db.execute(select(User).filter(User.id == user_id, User.is_active == True, User.is_deleted == False))
        return result.scalars().first()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        logger.debug(f"Fetching user by email: {email}")
        result = await db.execute(select(User).filter(User.email == email, User.is_active == True, User.is_deleted == False))
        return result.scalars().first()

    @staticmethod
    async def update_user(db: AsyncSession, user: User) -> User:
        logger.debug(f"Updating user: {user.email}")
        await db.merge(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User updated successfully: {user.email}")
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user: User) -> None:
        """Soft delete user by setting is_active to False and is_deleted to True"""
        logger.debug(f"Deleting user: {user.email}")
        user.is_active = False
        user.is_deleted = True
        await db.merge(user)
        await db.commit()
        logger.info(f"User deleted successfully: {user.email}")
        
    @staticmethod
    async def is_last_admin(db: AsyncSession) -> bool:
        logger.debug("Checking if there are any active admin users left")
        result = await db.execute(select(User).filter(User.is_admin == True, User.is_active == True, User.is_deleted == False))
        admins = result.scalars().all()
        return len(admins) == 1
        
