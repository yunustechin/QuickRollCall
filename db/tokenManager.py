from redis.asyncio import Redis
import redis.exceptions
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class TokenManager:
    _ACCESS_TOKEN_KEY_PREFIX = "access_token:{}"

    def __init__(self, client: Redis):
        self.client = client

    def _set_token_sync(self, token: str, session_id: str, expire_seconds: int):
        """Executes the blocking Redis command to store a token with expiration."""
        key = self._ACCESS_TOKEN_KEY_PREFIX.format(token)
        self.client.setex(name=key, time=expire_seconds, value=session_id)

    def _consume_token_sync(self, token: str) -> Optional[str]:
        """Atomically retrieves and deletes a token using a synchronous pipeline."""
        key = self._ACCESS_TOKEN_KEY_PREFIX.format(token)
        with self.client.pipeline() as pipe:
            pipe.get(key)
            pipe.delete(key)
            results = pipe.execute()
        return results[0] if results else None

    async def set_token(self, token: str, session_id: str, expire_seconds: int) -> bool:
        """
        Stores a one-time access token with an expiration.
        This operation is executed in a separate thread to avoid blocking.

        Args:
            token (str): The unique token key.
            session_id (str): The session ID to associate with the token.
            expire_seconds (int): The token's time-to-live in seconds.

        Returns:
            bool: True if the token was set successfully, otherwise False.
        """
        try:
            await asyncio.to_thread(self._set_token_sync, token, session_id, expire_seconds)
            logger.info(f"Set access token for session {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Failed to set access token for session {session_id}: {e}")
            return False

    async def consume_token(self, token: str) -> Optional[str]:
        """
        Retrieves a token's session ID and immediately deletes it atomically.
        This operation is executed in a separate thread to avoid blocking.

        Args:
            token (str): The token to consume.

        Returns:
            Optional[str]: The session_id if the token exists, otherwise None.
        """
        try:
            session_id = await asyncio.to_thread(self._consume_token_sync, token)
            if session_id:
                logger.info(f"Successfully consumed token for session {session_id}")
            else: 
                logger.warning(f"Attempted to consume an invalid or expired token.")
            return session_id
        except redis.exceptions.RedisError as e:
            logger.error(f"Error consuming token: {e}")
            return None
