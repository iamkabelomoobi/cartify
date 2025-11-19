import json
from app.core.config import settings


def create_token_keys(user_id: str):
    """Create Redis keys for access and refresh tokens"""
    return {
        "access": f"token:{user_id}:access",
        "refresh": f"token:{user_id}:refresh",
    }


def store_tokens_redis(
    redis_client, user_id: str, access_token: str, refresh_token: str
) -> None:
    """Store access and refresh tokens in Redis with appropriate TTLs"""
    keys = create_token_keys(user_id)

    access_ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    redis_client.setex(keys["access"], access_ttl, access_token)

    refresh_ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    redis_client.setex(keys["refresh"], refresh_ttl, refresh_token)


def get_tokens_redis(redis_client, user_id: str) -> dict | None:
    keys = create_token_keys(user_id)

    refresh_token = redis_client.get(keys["refresh"])

    if not refresh_token:
        delete_tokens_redis(redis_client, user_id)
        return None

    access_token = redis_client.get(keys["access"])

    if not access_token:
        return {"refresh_token": refresh_token}

    return {"access_token": access_token, "refresh_token": refresh_token}


def delete_tokens_redis(redis_client, user_id: str) -> None:
    """Delete both access and refresh tokens from Redis"""
    keys = create_token_keys(user_id)
    redis_client.delete(keys["access"], keys["refresh"])
