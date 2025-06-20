from fastapi import Depends
from functools import lru_cache
from db import RedisClient
from .services import SessionService

@lru_cache(maxsize=1)
def get_redis_client() -> RedisClient:
    """
    Provides a singleton RedisClient instance for the application.

    Uses @lru_cache to ensure a single, efficient connection is shared.
    """
    return RedisClient()

def get_session_service(redis: RedisClient = Depends(get_redis_client)) -> SessionService: 
    """
    Dependency provider for the SessionService.

    Initializes the service with required dependencies (like RedisClient)
    for easy use in route handlers.
    """
    return SessionService(redis)
