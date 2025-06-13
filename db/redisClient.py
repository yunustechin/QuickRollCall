import redis
import os
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedisClient:
    """
    A client class to handle all interactions with the Redis database for the
    QR attendance application. It manages connection, session creation, and
    student data records.
    """

    _SESSION_KEY_PREFIX = "session:{}"
    _ATTENDANCE_KEY_PREFIX = "attendance:{}"
    _SESSION_STATUS_FIELD = "status"
    _SESSION_OPEN_STATUS = "open"
    _SESSION_CLOSED_STATUS = "closed"

    def __init__(self):
        """
        Initializes the Redis client.
        
        Connection parameters are sourced from environment variables to allow for
        flexible deployment, with sensible defaults for local development.
        """
        redis_host = os.environ.get("REDIS_HOST", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))
        self.client: Optional[redis.Redis] = None

        try:
            logger.info(f"Attempting to connect to Redis at {redis_host}:{redis_port}...")
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=0,
                decode_responses=True,
                socket_connect_timeout=3
            )
            self.client.ping()
            logger.info("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            logger.critical(f"Failed to connect to Redis at {redis_host}:{redis_port}. Error: {e}")
            logger.critical("Ensure Redis is running and accessible. The application might not function correctly.")
            self.client = None

    def _is_client_available(self) -> bool:
        """Checks if the Redis client is connected."""
        if not self.client:
            logger.warning("Redis client is not available. Operation cancelled.")
            return False
        return True

    def create_attendance_session(self, session_id: str, expires_in_seconds: int = 300) -> bool:
        """
        Creates a new attendance session in Redis, marked as 'open', with an expiration time.

        Args:
            session_id (str): The unique identifier for the session.
            expires_in_seconds (int): The session's lifespan in seconds. Defaults to 300 (5 minutes).

        Returns:
            bool: True if the session was created successfully, False otherwise.
        """
        if not self._is_client_available():
            return False
        
        session_key = self._SESSION_KEY_PREFIX.format(session_id)
        try:
            pipe = self.client.pipeline(transaction=True)
            pipe.hset(session_key, self._SESSION_STATUS_FIELD, self._SESSION_OPEN_STATUS)
            pipe.expire(session_key, expires_in_seconds)
            pipe.execute()
            logger.info(f"Created new attendance session: {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Failed to create Redis session {session_id}. Error: {e}")
            return False

    def is_session_valid(self, session_id: str) -> bool:
        """
        Checks if a given session ID is valid and the session is currently open.

        Args:
            session_id (str): The session ID to validate.

        Returns:
            bool: True if the session exists and is 'open', False otherwise.
        """
        if not self._is_client_available():
            return False
        
        try:
            status = self.client.hget(self._SESSION_KEY_PREFIX.format(session_id), self._SESSION_STATUS_FIELD)
            return status == self._SESSION_OPEN_STATUS
        except redis.exceptions.RedisError as e:
            logger.error(f"Error validating session {session_id}. Error: {e}")
            return False

    def has_student_submitted(self, session_id: str, student_id: str) -> bool:
        """
        Checks if a student has already submitted their attendance for a specific session.

        Args:
            session_id (str): The session identifier.
            student_id (str): The unique identifier for the student (e.g., school number).

        Returns:
            bool: True if a record for the student exists in this session, False otherwise.
        """
        if not self._is_client_available():
            return False
        
        try:
            attendance_key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
            return self.client.hexists(attendance_key, student_id)
        except redis.exceptions.RedisError as e:
            logger.error(f"Error checking student {student_id} submission for session {session_id}. Error: {e}")
            return False

    def add_student_record(self, session_id: str, student_id: str, student_data: Dict[str, Any]) -> bool:
        """
        Adds a student's attendance record to the specified session.

        Args:
            session_id (str): The session identifier.
            student_id (str): The student's unique identifier.
            student_data (Dict[str, Any]): A dictionary containing the student's information.

        Returns:
            bool: True if the record was added successfully, False otherwise.
        """
        if not self._is_client_available():
            return False
        
        try:
            attendance_key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
            serialized_data = json.dumps(student_data)
            self.client.hset(attendance_key, student_id, serialized_data)
            logger.info(f"Added record for student {student_id} to session {session_id}.")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Failed to add record for student {student_id} to session {session_id}. Error: {e}")
            return False
