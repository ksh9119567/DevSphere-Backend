import logging

from sqlalchemy.future import select

from app.core.repository import BaseRepository
from app.core.exception import NotFoundException

from app.modules.users.models import User, UserFollow

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):

    async def create_user(self, user: User) -> User:
        logger.debug(f"Creating user: {user.email}")
        user = await self.create(user)
        logger.info(f"User created successfully with email: {user.email}")
        return user

    async def get_all_users(self) -> list[User]:
        logger.debug("Fetching all users")

        query = select(User)

        return await self.get_all(query)

    async def get_all_users_except_admins(self) -> list[User]:
        logger.debug("Fetching all non-admin users")

        query = select(User).filter(
            User.is_admin == False,
            User.is_deleted == False
        )

        return await self.get_all(query)

    async def get_user_by_id(self, user_id: int, is_admin: bool) -> User:
        logger.debug(f"Fetching user by id: {user_id}")

        if is_admin:
            query = select(User).filter(
                User.id == user_id
            )
        else:
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
    
    async def follow_user(self, follow: UserFollow) -> UserFollow:
        # Fetch the follower and following users
        follower = await self.get_user_by_id(follow.follower_id)
        following = await self.get_user_by_id(follow.following_id)
        
        if not follower or not following:
            logger.warning(f"Either follower (ID: {follow.follower_id}) or following (ID: {follow.following_id}) user does not exist")
            raise NotFoundException("Follower or following user does not exist")
        
        follow = await self.create(follow)
        
        follower.following_count += 1
        await self.update_user(follower)
        
        following.follower_count += 1
        await self.update_user(following)
        
        logger.info(f"User {follow.follower_id} followed user {follow.following_id}")
        return follow
    
    async def unfollow_user(self, follower_id: int, following_id: int) -> str:
        # Fetch the follower, following users and the follow relationship
        follower = await self.get_user_by_id(follower_id)
        following = await self.get_user_by_id(following_id)
        
        if not follower or not following:
            logger.warning(f"Either follower (ID: {follower_id}) or following (ID: {following_id}) user does not exist")
            raise NotFoundException("Follower or following user does not exist")
        
        query = select(UserFollow).filter(
            UserFollow.follower_id == follower_id,
            UserFollow.following_id == following_id
        )
        follow = await self.get_one(query)
        
        if not follow:
            logger.warning(f"Follow relationship between follower (ID: {follower_id}) and following (ID: {following_id}) does not exist")
            raise NotFoundException("Follow relationship does not exist")
        
        await self.delete(follow)
        
        follower.following_count -= 1
        await self.update_user(follower)
        
        following.follower_count -= 1
        await self.update_user(following)
        
        logger.info(f"User {follower_id} unfollowed user {following_id}")
        return {"message": "Unfollowed successfully"}
    
    async def get_followers(self, user_id: int) -> list[User]:
        logger.debug(f"Fetching followers for user ID: {user_id}")

        query = select(User).join(UserFollow, User.id == UserFollow.follower_id).filter(
            UserFollow.following_id == user_id,
            User.is_active == True,
            User.is_deleted == False
        )

        return await self.get_all(query)
    
    async def get_following(self, user_id: int) -> list[User]:
        logger.debug(f"Fetching following for user ID: {user_id}")

        query = select(User).join(UserFollow, User.id == UserFollow.following_id).filter(
            UserFollow.follower_id == user_id,
            User.is_active == True,
            User.is_deleted == False
        )

        return await self.get_all(query)
        