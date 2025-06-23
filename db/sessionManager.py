from redis.asyncio import Redis
import redis.exceptions
import logging
import asyncio

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages the lifecycle of attendance sessions in Redis."""
    _SESSION_KEY_PREFIX = "session:{}"
    _SESSION_STATUS_FIELD = "status"
    _SESSION_OPEN_STATUS = "open"
    _SESSION_CLOSED_STATUS = "closed"

    def __init__(self, client: Redis):
        self.client = client

    def _create_session_sync(self, session_id: str, expires_in_seconds: int):
        """
        Executes the blocking Redis commands to create a new session.
        Uses a pipeline to ensure atomicity.
        """
        key = self._SESSION_KEY_PREFIX.format(session_id)
        with self.client.pipeline(transaction=True) as pipe:
            pipe.hset(key, self._SESSION_STATUS_FIELD, self._SESSION_OPEN_STATUS)
            pipe.expire(key, expires_in_seconds)
            pipe.execute()

    def _close_session_sync(self, session_id: str):
        """
        Executes the blocking Redis commands to close a session.
        Uses a pipeline to ensure atomicity.
        """
        key = self._SESSION_KEY_PREFIX.format(session_id)
        with self.client.pipeline(transaction=True) as pipe:
            pipe.hset(key, self._SESSION_STATUS_FIELD, self._SESSION_CLOSED_STATUS)
            pipe.persist(key) 
            pipe.execute()

    def _is_session_valid_sync(self, session_id: str) -> bool:
        """
        Executes the blocking Redis command to check if a session is open.
        """
        key = self._SESSION_KEY_PREFIX.format(session_id)
        status = self.client.hget(key, self._SESSION_STATUS_FIELD)
        return status == self._SESSION_OPEN_STATUS

    async def create_session(self, session_id: str, expires_in_seconds: int = 300) -> bool:
        """
        Creates a new session with an 'open' status and a TTL.

        This method safely executes the synchronous, blocking database
        operations in a separate thread.
        
        Args:
            session_id (str): The unique identifier for the session.
            expires_in_seconds (int): The session's time-to-live in seconds.

        Returns:
            bool: True if the session was created successfully, otherwise False.
        """
        try:
            await asyncio.to_thread(
                self._create_session_sync, session_id, expires_in_seconds
            )
            logger.info(f"Created session {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Create session failed for {session_id}: {e}")
            return False

    async def close_session(self, session_id: str) -> bool:
        """
        Closes a session by marking its status as 'closed' and removing its TTL.
        
        This method safely executes the synchronous, blocking database
        operations in a separate thread.

        Args:
            session_id (str): The identifier of the session to close.

        Returns:
            bool: True if the session was closed successfully, otherwise False.
        """
        try:
            await asyncio.to_thread(self._close_session_sync, session_id)
            logger.info(f"Closed session {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Close session failed for {session_id}: {e}")
            return False

    async def is_session_valid(self, session_id: str) -> bool:
        """
        Checks if a session exists and its status is 'open'.

        This method safely executes the synchronous, blocking database
        operation in a separate thread.
        
        Args:
            session_id (str): The identifier of the session to validate.

        Returns:
            bool: True if the session is valid and open, otherwise False.
        """
        try:
            return await asyncio.to_thread(self._is_session_valid_sync, session_id)
        except redis.exceptions.RedisError as e:
            logger.error(f"Session validation failed for {session_id}: {e}")
            return False
