import os
import logging
import json

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.db.database import get_db
from app.core.redis_manager import redis_client
from app.core.repositories.user_repository import UserRepository

load_dotenv()

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Invalid token: no email in payload")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise credentials_exception

    # Check if token exists in Redis (token blacklist check)
    stored_token_json = await redis_client.get(f"access_token:{email}")
    if stored_token_json is None:
        logger.warning(f"Access token not found in Redis for user: {email} (possibly logged out)")
        raise credentials_exception
    
    # Parse JSON payload
    try:
        token_data = json.loads(stored_token_json)
        stored_token = token_data.get("token")
    except (json.JSONDecodeError, KeyError):
        logger.warning(f"Invalid token data format in Redis for user: {email}")
        raise credentials_exception
    
    if stored_token != token:
        logger.warning(f"Access token mismatch for user: {email}")
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)
    if user is None:
        logger.warning(f"User not found in database: {email}")
        raise credentials_exception
    logger.debug(f"User authenticated: {email}")
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user
