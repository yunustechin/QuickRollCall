from redis.asyncio import Redis
import redis.exceptions
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TokenManager:
    _ACCESS_TOKEN_KEY_PREFIX = "access_token:{}"

    def __init__(self, client: Redis):
        self.client = client

    async def set_token(self, token: str, session_id: str, expire_seconds: int) -> bool:
        """
        Stores a one-time access token with an expiration.

        Args:
            token (str): The unique token key.
            session_id (str): The session ID to associate with the token.
            expire_seconds (int): The token's time-to-live in seconds.

        Returns:
            bool: True if the token was set successfully.

        Raises:
            redis.exceptions.RedisError: If the Redis command fails.
        """
        key = self._ACCESS_TOKEN_KEY_PREFIX.format(token)
        try:
            await self.client.setex(name=key, time=expire_seconds, value=session_id)
            logger.info(f"Set access token for session {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Failed to set access token for session {session_id}: {e}")
            return False

    async def consume_token(self, token: str) -> Optional[str]:
        """
        Retrieves a token's session ID and immediately deletes the token (atomically).

        Args:
            token (str): The token to consume.

        Returns:
            Optional[str]: The session_id if the token exists, otherwise None.

        Raises:
            redis.exceptions.RedisError: If the Redis pipeline execution fails.
        """
        key = self._ACCESS_TOKEN_KEY_PREFIX.format(token)
        try:
            async with self.client.pipeline() as pipe:
                await pipe.get(key)
                await pipe.delete(key)
                results = await pipe.execute()
            session_id = results[0]

            if session_id:
                logger.info(f"Successfully consumed token for session {session_id}")
            
            else: 
                logger.warning(f"Attempted to consume an invalid or expired token.")
                
            return session_id 
        except redis.exceptions.RedisError as e:
            logger.error(f"Error consuming token: {e}")
            raise
            
