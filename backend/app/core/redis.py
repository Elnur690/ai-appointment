import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None

    async def init_redis(self):
        self._pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        self._client = redis.Redis.from_pool(self._pool)

    async def close_redis(self):
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.disconnect()

    def get_redis(self) -> redis.Redis:
        if not self._client:
            raise RuntimeError("Redis connection not initialized")
        return self._client

redis_client = RedisClient()

async def init_redis():
    await redis_client.init_redis()

async def close_redis():
    await redis_client.close_redis()

def get_redis() -> redis.Redis:
    return redis_client.get_redis()
