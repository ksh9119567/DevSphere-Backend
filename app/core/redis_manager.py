# app/core/redis_manager.py
import logging
import redis.asyncio as redis
import os

logger = logging.getLogger(__name__)

# In production, load from .env
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info(f"Redis client initialized with URL: {REDIS_URL}")
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {str(e)}")
    raise
