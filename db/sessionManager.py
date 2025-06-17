from redis.asyncio import Redis
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
        """Create a new session with 'open' status and a TTL."""
        key = self._SESSION_KEY_PREFIX.format(session_id)
        try:
            async with self.client.pipeline(transaction=True) as pipe:
                await pipe.hset(key, self._SESSION_STATUS_FIELD, self._SESSION_OPEN_STATUS)
                await pipe.expire(key, expires_in_seconds)
                await pipe.execute()
            logger.info(f"Created session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Create session failed for {session_id}: {e}")
            return False

    async def close_session(self, session_id: str) -> bool:
        """Close the session by marking its status 'closed' and removing TTL."""
        key = self._SESSION_KEY_PREFIX.format(session_id)
        try:
            async with self.client.pipeline(transaction=True) as pipe:
                await pipe.hset(key, self._SESSION_STATUS_FIELD, self._SESSION_CLOSED_STATUS)
                await pipe.persist(key)  # Remove TTL
                await pipe.execute()
            logger.info(f"Closed session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Close session failed for {session_id}: {e}")
            return False

    async def is_session_valid(self, session_id: str) -> bool:
        """Check if the session status is currently 'open'."""
        key = self._SESSION_KEY_PREFIX.format(session_id)
        try:
            status = await self.client.hget(key, self._SESSION_STATUS_FIELD)
            return status == self._SESSION_OPEN_STATUS
        except Exception as e:
            logger.error(f"Session validation failed for {session_id}: {e}")
            return False
