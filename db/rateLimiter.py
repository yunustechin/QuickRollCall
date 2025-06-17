from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    _RATE_LIMIT_KEY_PREFIX = "rate_limit:{}"

    def __init__(self, client: Redis):
        self.client = client

    async def is_limited(self, client_id: str, limit: int, window: int) -> bool:
        """Check if a client exceeded the request limit within a time window using Redis counters."""
        key = self._RATE_LIMIT_KEY_PREFIX.format(client_id)
        try:
            async with self.client.pipeline(transaction=False) as pipe:
                await pipe.incr(key)
                await pipe.expire(key, window, nx=True)
                results = await pipe.execute()
            count = results[0]
            limited = count > limit
            if limited:
                logger.warning(f"Rate limit exceeded for client {client_id} ({count} > {limit})")
            return limited
        except Exception as e:
            logger.error(f"Rate limit check failed for client {client_id}: {e}")
            return False
