import redis
from app.core.config import settings
import logging

logger = logging.getLogger("uvicorn.error")

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


def get_redis():
    return redis_client


def ping_redis() -> bool:
    try:
        redis_client.ping()
        logger.info("Redis connection successful.")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False
