import logging
import random
import string

from app.core.redis_manager import redis_client

logger = logging.getLogger(__name__)

REDIX_PREFIX = "email_otp:"
RESET_OTP_TTL = 60 * 5


def _make_key(email: str) -> str:
    return f"{REDIX_PREFIX}{email}"

async def generate_otp(length: int = 6) -> str:
    otp = ''.join(random.choices(string.digits, k=length))
    logger.info(f"Generated OTP: {otp}")
    return otp
    
async def store_otp(email: str, otp: str):
    key = _make_key(email)
    await redis_client.set(key, otp, ex=RESET_OTP_TTL)
    logger.info(f"Stored OTP for email: {email}")

async def delete_otp(email:str):
    key = _make_key(email)
    await redis_client.delete(key)
    logger.info(f"Deleted OTP for email: {email}")

async def get_otp(email:str) -> str:
    logger.info(f"Getting otp for email: {email}")
    key = _make_key(email)
    val = await redis_client.get(key)
    if not val:
        logger.warning(f"OTP not found for email: {email}")
        raise Exception(f"OTP not found for email: {email}")
    try:
        return val.decode("utf-8")
    except Exception:
        return str(val)
    
async def get_attempts(email: str) -> int:
    key = f"{_make_key(email)}:attempts"
    attempts = await redis_client.get(key)
    return int(attempts) if attempts else 0

async def increment_attempt(email: str, window_seconds: int = 60):
    key = f"{_make_key(email)}:attempts"
    attempts = await redis_client.incr(key)
    if attempts == 1:
        await redis_client.expire(key, window_seconds)
    logger.info(f"Attempt {attempts} for email: {email}")
    return attempts

async def reset_attempts(email: str):
    key = f"{_make_key(email)}:attempts"
    await redis_client.delete(key)
    logger.info(f"Reset attempts for email: {email}")