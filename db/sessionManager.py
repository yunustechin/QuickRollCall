from redis.asyncio import Redis
import redis.exceptions
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    _SESSION_KEY_PREFIX = "session:{}"
    _SESSION_STATUS_FIELD = "status"
    _SESSION_OPEN_STATUS = "open"
    _SESSION_CLOSED_STATUS = "closed"

    def __init__(self, client: Redis):
        self.client = client

    async def create_session(self, session_id: str, expires_in_seconds: int = 300) -> bool:
        """
        Creates a new session with an 'open' status and a TTL.

        Args:
            session_id (str): The unique identifier for the session.
            expires_in_seconds (int): The session's time-to-live in seconds.

        Returns:
            bool: True if the session was created successfully.

        Raises:
            redis.exceptions.RedisError: If a Redis command fails.
        """
        key = self._SESSION_KEY_PREFIX.format(session_id)
        try:
            async with self.client.pipeline(transaction=True) as pipe:
                await pipe.hset(key, self._SESSION_STATUS_FIELD, self._SESSION_OPEN_STATUS)
                await pipe.expire(key, expires_in_seconds)
                await pipe.execute()
            logger.info(f"Created session {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Create session failed for {session_id}: {e}")
            return False

    async def close_session(self, session_id: str) -> bool:
        """
        Closes a session by marking its status as 'closed' and removing its TTL.

        Args:
            session_id (str): The identifier of the session to close.

        Returns:
            bool: True if the session was closed successfully.

        Raises:
            redis.exceptions.RedisError: If a Redis command fails.
        """
        key = self._SESSION_KEY_PREFIX.format(session_id)
        try:
            async with self.client.pipeline(transaction=True) as pipe:
                await pipe.hset(key, self._SESSION_STATUS_FIELD, self._SESSION_CLOSED_STATUS)
                await pipe.persist(key)  # Remove TTL
                await pipe.execute()
            logger.info(f"Closed session {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Close session failed for {session_id}: {e}")
            return False

    async def is_session_valid(self, session_id: str) -> bool:
        """
        Checks if a session exists and its status is 'open'.

        Args:
            session_id (str): The identifier of the session to validate.

        Returns:
            bool: True if the session is valid and open, otherwise False.

        Raises:
            redis.exceptions.RedisError: If the Redis command fails.
        """
        key = self._SESSION_KEY_PREFIX.format(session_id)
        try:
            status = await self.client.hget(key, self._SESSION_STATUS_FIELD)
            return status == self._SESSION_OPEN_STATUS
        except redis.exceptions.RedisError as e:
            logger.error(f"Session validation failed for {session_id}: {e}")
            return False
