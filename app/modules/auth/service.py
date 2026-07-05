import logging

from app.events import event_dispatcher
from app.events.events.user_events import EmailOTPRequestedEvent
from app.core.redis_manager import redis_client
from app.core.exception import AuthenticationException
from app.modules.users.repositories.user_repository import UserRepository
from app.core.response import success_response
from app.services.base_service import BaseService
from app.services import otp_service
from app.services.token_service import (
    verify_password, create_access_token, create_refresh_token, verify_and_refresh_token
)

logger = logging.getLogger(__name__)


class AuthService(BaseService):

    def __init__(self, db):
        super().__init__(db)
        self.user_repo = UserRepository(db)

    async def _generate_tokens(
            self, user
        ) -> dict:
        
        """Generate access and refresh tokens for a user"""
        user_info = {
            "user_id": str(user.id),
            "is_admin": user.is_admin,
            "is_email_verified": user.is_email_verified
        }

        access_token = await create_access_token(
            data={"sub": user.email},
            user_info=user_info
        )

        refresh_token = await create_refresh_token(
            data={"sub": user.email},
            user_info=user_info
        )

        return success_response(
            "Tokens generated successfully",
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        )

    async def login(
            self, email: str, password: str
        ) -> dict:
        
        logger.info(f"Login attempt for email: {email}")

        user = await self.user_repo.get_user_by_email(email)

        if not user or not verify_password(password, user.password):
            raise AuthenticationException("Invalid credentials")

        return await self._generate_tokens(user)

    async def refresh(
            self, refresh_token: str
        ) -> dict:
        
        if not refresh_token:
            raise AuthenticationException("Refresh token is required")

        tokens = await verify_and_refresh_token(refresh_token)
        return success_response("Token refreshed successfully", tokens)

    async def logout(
            self, user_email: str
        ) -> dict:
        
        await redis_client.delete(f"access_token:{user_email}")
        await redis_client.delete(f"refresh_token:{user_email}")

        return success_response("Logged out successfully")
    
    async def send_otp(
            self, email: str, request_type: str = "verification"
        ):
        
        if request_type not in ["login", "resend", "verification"]:
            raise AuthenticationException("Invalid request type")
        
        # For login requests, user must exist and be email verified
        if request_type == "login":
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                raise AuthenticationException("User not found")
            if not user.is_email_verified:
                raise AuthenticationException("Email not verified")
        
        # Check current attempts before processing
        current_attempts = await otp_service.get_attempts(email)
        if current_attempts >= 5:
            logger.warning(f"Too many attempts for email: {email}")
            raise AuthenticationException("Too many attempts. Please try again later.")
        
        # Reset attempts if this is a resend request
        if request_type == "resend":
            await otp_service.reset_attempts(email)
            current_attempts = 0
        
        # Delete previous OTP if this is a retry (not first attempt)
        if current_attempts > 0:
            await otp_service.delete_otp(email)
        
        # Generate and store new OTP
        otp = await otp_service.generate_otp()
        await otp_service.store_otp(email, otp)
        
        # Increment attempt counter
        await otp_service.increment_attempt(email)
        
        # Dispatch event and capture task ID
        dispatch_result = await event_dispatcher.dispatch(EmailOTPRequestedEvent(email=email, otp=otp))
        task_id = None
        if dispatch_result and len(dispatch_result) > 0:
            task_id = dispatch_result[0].get("task_id")
        
        logger.info(f"OTP sent to email: {email}, task_id: {task_id}")
        return success_response("OTP sent successfully", task_id=task_id)
    
    async def verify_otp(
            self, email: str, otp: str
        ):
        
        stored_otp = await otp_service.get_otp(email)
        if stored_otp != otp:
            raise AuthenticationException("Invalid OTP")
        
        await otp_service.delete_otp(email)
        await otp_service.reset_attempts(email)
        logger.info(f"OTP verified for email: {email}")
        return success_response("OTP verified successfully")

    async def otp_login(
            self, email: str, otp: str
        ):
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise AuthenticationException("User not found")
        
        if not user.is_email_verified:
            raise AuthenticationException("Email not verified")
        
        stored_otp = await otp_service.get_otp(email)
        if stored_otp != otp:
            raise AuthenticationException("Invalid OTP")
        
        await otp_service.delete_otp(email)
        await otp_service.reset_attempts(email)
        
        logger.info(f"OTP login successful for email: {email}")
        return await self._generate_tokens(user)