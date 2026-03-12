import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.modules.users.models import User
from app.core.redis_manager import redis_client
from app.services.token_service import (verify_password, create_access_token, 
    create_refresh_token, verify_and_refresh_token)
from app.core.exception import AuthenticationException
from app.core.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def login(email: str, password: str, db: AsyncSession) -> dict:
        logger.info(f"Login attempt for email: {email}")
        user = await UserRepository.get_user_by_email(db, email)
        if not user or not verify_password(password, user.password):
            logger.warning(f"Failed login attempt for email: {email}")
            raise AuthenticationException("Invalid credentials")

        user_info = {
            "user_id": str(user.id),
            "is_admin": user.is_admin,
            "is_email_verified": user.is_email_verified
        }
        
        access_token = await create_access_token(data={"sub": user.email}, user_info=user_info)
        refresh_token = await create_refresh_token(data={"sub": user.email}, user_info=user_info)
        logger.info(f"User logged in successfully: {email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def refresh(refresh_token: str) -> dict:
        logger.info("Refresh token request received")
        if not refresh_token:
            logger.warning("No refresh token provided")
            raise AuthenticationException("Refresh token is required")
        
        return await verify_and_refresh_token(refresh_token)

    @staticmethod
    async def logout(user_email: str) -> dict:
        await redis_client.delete(f"access_token:{user_email}")
        await redis_client.delete(f"refresh_token:{user_email}")
        logger.info(f"User logged out successfully: {user_email}")
        return {"message": "Logged out successfully"}
