from redis.asyncio import Redis
import redis.exceptions
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    _RATE_LIMIT_KEY_PREFIX = "rate_limit:{}"

    def __init__(self, client: Redis):
        self.client = client

    async def is_limited(self, client_id: str, limit: int, window: int) -> bool:
        """
        Checks if a client has exceeded the request limit within a time window.

        This method uses the sliding window counter algorithm. It increments a
        counter for the client and checks if it exceeds the defined limit.

        Args:
            client_id (str): A unique identifier for the client (e.g., an IP address).
            limit (int): The maximum number of requests allowed in the window.
            window (int): The duration of the time window in seconds.

        Returns:
            bool: True if the client is rate-limited, otherwise False.

        Raises:
            redis.exceptions.RedisError: If the Redis command fails. This is a
                "fail-safe" approach; the caller should handle the error, likely
                by blocking the request.
        """
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
        except redis.exceptions.RedisError as e:
            logger.error(f"Rate limit check failed for client {client_id}: {e}")
            raise
