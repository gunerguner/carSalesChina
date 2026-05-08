import redis.asyncio as aioredis

from backend.config import REDIS_URL

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


async def close_redis():
    if redis_client:
        await redis_client.close()