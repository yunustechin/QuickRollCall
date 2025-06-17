import redis.asyncio as redis
import os
import logging

logger = logging.getLogger(__name__)

def create_redis_client() -> redis.Redis:
    """Create and return an async Redis client using a connection pool."""
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
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise e
