import json
import logging
from typing import Any

from backend.src.core.redis_client import get_redis

logger = logging.getLogger(__name__)


async def get_cache(key: str) -> dict[str, Any] | None:
    redis = await get_redis()
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cache(key: str, value: dict[str, Any], ttl: int = 3600) -> None:
    redis = await get_redis()
    await redis.setex(key, ttl, json.dumps(value, ensure_ascii=False))


async def delete_cache(pattern: str) -> None:
    redis = await get_redis()
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)