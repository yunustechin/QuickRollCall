from db import RedisClient
from functools import lru_cache

@lru_cache(maxsize=1)
def get_redis_client() -> RedisClient:
    """
    Returns a singleton instance of the RedisClient.
    """
    return RedisClient()
