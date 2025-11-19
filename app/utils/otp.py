import random
import string
import json
from datetime import datetime, timedelta, timezone


def generate_otp() -> str:
    """Generate a 6-digit numeric OTP"""
    return "".join(random.choices(string.digits, k=6))


def get_otp_ttl_seconds() -> int:
    """OTP TTL in seconds (10 minutes)"""
    return 10 * 60


def create_otp_key(user_id: str) -> str:
    """Create Redis key for OTP using user_id"""
    return f"otp:{user_id}"


def store_otp_redis(redis_client, user_id: str, otp_code: str) -> None:
    """Store OTP in Redis with TTL"""
    key = create_otp_key(user_id)
    value = json.dumps(
        {
            "user_id": user_id,
            "code": otp_code,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    redis_client.setex(key, get_otp_ttl_seconds(), value)


def get_otp_redis(redis_client, user_id: str) -> dict | None:
    """Retrieve OTP from Redis"""
    key = create_otp_key(user_id)
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None


def delete_otp_redis(redis_client, user_id: str) -> None:
    """Delete OTP from Redis"""
    key = create_otp_key(user_id)
    redis_client.delete(key)
