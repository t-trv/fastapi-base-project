import json
from typing import Any, Optional
import redis.asyncio as aioredis
from app.config.settings import settings
from app.utils.log import log_info, log_error

# 1. Initialize Redis Client
redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> Optional[aioredis.Redis]:
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5.0,
        )
        await redis_client.ping()
        log_info("redis", f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return redis_client
    except Exception as e:
        log_error("redis", f"Failed to connect to Redis: {e}")
        redis_client = None
        return None


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        log_info("redis", "Redis connection closed.")


async def get_redis() -> Optional[aioredis.Redis]:
    return redis_client


# 2. Cache Helper Methods
async def get_cache(key: str) -> Optional[Any]:
    if not redis_client:
        return None
    try:
        val = await redis_client.get(key)
        if val is not None:
            return json.loads(val)
    except Exception as e:
        log_error("redis", f"Error getting cache for key '{key}': {e}")
    return None


async def set_cache(key: str, value: Any, expire: int = 60) -> bool:
    if not redis_client:
        return False
    try:
        serialized = json.dumps(value, default=str)
        await redis_client.set(key, serialized, ex=expire)
        return True
    except Exception as e:
        log_error("redis", f"Error setting cache for key '{key}': {e}")
        return False


async def delete_cache_pattern(pattern: str) -> int:
    if not redis_client:
        return 0
    try:
        keys = []
        async for key in redis_client.scan_iter(pattern):
            keys.append(key)
        if keys:
            return await redis_client.delete(*keys)
    except Exception as e:
        log_error("redis", f"Error deleting cache pattern '{pattern}': {e}")
    return 0
