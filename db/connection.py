import redis.asyncio as redis
import redis.exceptions
import os
import logging

logger = logging.getLogger(__name__)

def create_redis_client() -> redis.Redis:
    """
    Creates and returns an asynchronous Redis client using a connection pool.

    This function reads connection details (host, port) from environment
    variables and establishes a robust connection pool for efficient
    Redis communication.

    Returns:
        redis.Redis: An initialized asynchronous Redis client instance.

    Raises:
        redis.exceptions.ConnectionError: If the connection to the Redis server fails
                                     during initialization.
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    try:
        pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=0,
            decode_responses=True,
            socket_connect_timeout=3
        )
        client = redis.Redis(connection_pool=pool)
        logger.info(f"Redis connection pool created at {host}:{port}")
        return client
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        raise

    
    
    
