import logging

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .service import AuthService

from app.modules.users.models import User
from app.db.database import get_db
from app.core.security import get_current_user
from app.core.exception import AuthenticationException

router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends(), 
                db: AsyncSession = Depends(get_db)):
    logger.info(f"User with email: {request.username} is attempting to log in")
    return await AuthService.login(request.username, request.password, db)

@router.post("/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    logger.info("Attempting to refresh access token")
    return await AuthService.refresh(refresh_token)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is attempting to log out")
    return await AuthService.logout(current_user.email)
