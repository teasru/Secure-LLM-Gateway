import redis
from fastapi import HTTPException
from app.config import settings


# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=6379,
    decode_responses=True,
)


def enforce_rate_limit(user_id: str):
    """
    Enforces per-user rate limiting using Redis.

    Uses:
    - settings.RATE_LIMIT  → max requests allowed
    - settings.RATE_WINDOW → time window in seconds
    """

    key = f"rate:{user_id}"

    try:
        # Increment request counter
        current_count = redis_client.incr(key)

        # If first request in window, set expiry
        if current_count == 1:
            redis_client.expire(key, settings.RATE_WINDOW)

        # If limit exceeded
        if current_count > settings.RATE_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

    except redis.RedisError:
        # If Redis fails, fail open (do not block request)
        # In production you might log this.
        pass
