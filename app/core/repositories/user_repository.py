import logging

from sqlalchemy.future import select

from .base_repository import BaseRepository

from app.modules.users.models import User

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):

    async def create_user(self, user: User) -> User:
        logger.debug(f"Creating user: {user.email}")
        user = await self.create(user)
        logger.info(f"User created successfully with email: {user.email}")
        return user

    async def get_all_users(self) -> list[User]:
        logger.debug("Fetching all users")

        query = select(User).filter(
            User.is_active == True,
            User.is_deleted == False
        )

        return await self.get_all(query)

    async def get_all_users_except_admins(self) -> list[User]:
        logger.debug("Fetching all non-admin users")

        query = select(User).filter(
            User.is_admin == False,
            User.is_deleted == False
        )

        return await self.get_all(query)

    async def get_user_by_id(self, user_id: int) -> User:
        logger.debug(f"Fetching user by id: {user_id}")

        query = select(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.is_deleted == False
        )

        return await self.get_one(query)

    async def get_user_by_email(self, email: str) -> User:
        logger.debug(f"Fetching user by email: {email}")

        query = select(User).filter(
            User.email == email,
            User.is_active == True,
            User.is_deleted == False
        )

        return await self.get_one(query)

    async def update_user(self, user: User) -> User:
        logger.debug(f"Updating user: {user.email}")
        user = await self.update(user)
        logger.info(f"User updated successfully: {user.email}")
        return user

    async def delete_user(self, user: User) -> None:
        logger.debug(f"Deleting user: {user.email}")

        await self.soft_delete(
            user,
            {
                "is_active": False,
                "is_deleted": True
            }
        )

        logger.info(f"User deleted successfully: {user.email}")

    async def is_last_admin(self) -> bool:
        logger.debug("Checking if there are any active admin users left")

        query = select(User).filter(
            User.is_admin == True,
            User.is_active == True,
            User.is_deleted == False
        )

        admins = await self.get_all(query)

        return len(admins) == 1