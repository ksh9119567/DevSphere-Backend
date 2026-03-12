import os
import logging
import json

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.redis_manager import redis_client

load_dotenv()

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_access_token(data: dict, expires_delta: timedelta | None = None, user_info: dict | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # store token with additional user info in Redis as JSON
    user_identifier = data.get("sub")
    token_data = {
        "token": token,
        "user_email": user_identifier,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **(user_info or {})  # Merge any additional user info
    }
    await redis_client.setex(
        f"access_token:{user_identifier}", 
        ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        json.dumps(token_data)
    )
    logger.debug(f"Access token created for user: {user_identifier}")
    
    return token

async def create_refresh_token(data: dict, user_info: dict | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    # store token with additional user info in Redis as JSON
    user_identifier = data.get("sub")
    token_data = {
        "token": token,
        "user_email": user_identifier,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **(user_info or {})  # Merge any additional user info
    }
    await redis_client.setex(
        f"refresh_token:{user_identifier}", 
        REFRESH_TOKEN_EXPIRE_DAYS * 86400, 
        json.dumps(token_data)
    )
    logger.debug(f"Refresh token created and stored in Redis for user: {user_identifier}")

    return token

async def delete_access_token(user_email: str):
    await redis_client.delete(f"access_token:{user_email}")
    logger.debug(f"Access token deleted from Redis for user: {user_email}")
    
async def delete_refresh_token(user_email:str):
    await redis_client.delete(f"refresh_token:{user_email}")
    logger.debug(f"Refresh token deleted from Redis for user: {user_email}")

async def verify_and_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Invalid refresh token: no email in payload")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError as e:
        logger.warning(f"JWT verification failed for refresh token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    stored_token_json = await redis_client.get(f"refresh_token:{email}")
    if stored_token_json is None:
        logger.warning(f"Refresh token not found in Redis for user: {email}")
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")
    
    # Parse JSON payload
    try:
        token_data = json.loads(stored_token_json)
        stored_token = token_data.get("token")
    except (json.JSONDecodeError, KeyError):
        logger.warning(f"Invalid token data format in Redis for user: {email}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    if stored_token != refresh_token:
        logger.warning(f"Refresh token mismatch for user: {email}")
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

    await delete_access_token(email) # Invalidate old access token
    await delete_refresh_token(email) # Invalidate old refresh token
    
    user_info = {
        "user_id": token_data.get("user_id"),
        "is_admin": token_data.get("is_admin"),
        "is_email_verified": token_data.get("is_email_verified")
    }
    
    new_access_token = await create_access_token(data={"sub": email}, user_info=user_info)
    new_refresh_token = await create_refresh_token(data={"sub": email}, user_info=user_info)
    
    logger.info(f"Access token refreshed for user: {email}")
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
