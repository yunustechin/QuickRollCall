import logging
from typing import Dict, Optional
from .connection import create_redis_client
from .sessionManager import SessionManager
from .attendanceManager import AttendanceManager
from .rateLimiter import RateLimiter
from .tokenManager import TokenManager

logger = logging.getLogger(__name__)

class RedisClient:
    """The facade class that manages all Redis operations."""
    def __init__(self):
        self.client = create_redis_client()
        self._session_manager = SessionManager(self.client)
        self._attendance_manager = AttendanceManager(self.client)
        self._rate_limiter = RateLimiter(self.client)
        self._token_manager = TokenManager(self.client)
        logger.info("RedisClient initialized successfully.")
    
    async def ping(self) -> bool:
        """
        Checks the connection to the Redis server by sending a PING command.

        Returns:
            bool: True if the ping is successful, otherwise raises an exception.

        Raises:
            redis.exceptions.RedisError: If there is an issue with the connection
                                        or the server is unavailable.
            Exception: For any other unexpected errors during the ping operation.
        """
        logger.debug("Pinging Redis server...")
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            raise

    async def create_session(self, session_id: str, expires_in_seconds: int = 300) -> bool:
        return await self._session_manager.create_session(session_id, expires_in_seconds)

    async def close_session(self, session_id: str) -> bool:
        return await self._session_manager.close_session(session_id)

    async def is_session_valid(self, session_id: str) -> bool:
        return await self._session_manager.is_session_valid(session_id)

    async def has_student_submitted(self, session_id: str, student_id: str) -> bool:
        return await self._attendance_manager.has_submitted(session_id, student_id)

    async def add_student_record(self, session_id: str, student_id: str, student_data: Dict) -> bool:
        return await self._attendance_manager.add_record(session_id, student_id, student_data)

    async def export_attendance(self, session_id: str) -> Optional[Dict[str, Dict]]:
        return await self._attendance_manager.export_attendance(session_id)

    async def check_rate_limit(self, client_id: str, limit: int, window: int) -> bool:
        return await self._rate_limiter.is_limited(client_id, limit, window)
    
    async def set_access_token(self, token: str, session_id: str, expire_seconds: int) -> bool:
        return await self._token_manager.set_token(token, session_id, expire_seconds)

    async def consume_access_token(self, token: str) -> Optional[str]:
        return await self._token_manager.consume_token(token)