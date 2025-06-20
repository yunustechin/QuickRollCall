from redis.asyncio import Redis
import redis.exceptions
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AttendanceManager:
    _ATTENDANCE_KEY_PREFIX = "attendance:{}"

    def __init__(self, client: Redis):
        self.client = client

    async def has_submitted(self, session_id: str, student_id: str) -> bool:
        """
        Checks if a student has already submitted attendance for the given session.

        Args:
            session_id (str): The identifier for the session.
            student_id (str): The identifier for the student.

        Returns:
            bool: True if the student has submitted, otherwise False.

        Raises:
            redis.exceptions.RedisError: If the Redis command fails.
        """
        key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
        try:
            return await self.client.hexists(key, student_id)
        except redis.exceptions.RedisError as e:
            logger.error(f"Check submission failed for student {student_id} in session {session_id}: {e}")
            return False

    async def add_record(self, session_id: str, student_id: str, student_data: Dict) -> bool:
        """
        Adds or updates a student’s attendance record for a session.

        Args:
            session_id (str): The identifier for the session.
            student_id (str): The identifier for the student (to be used as the hash field).
            student_data (Dict): The student's data to store as a JSON string.

        Returns:
            bool: True if the record was added successfully.

        Raises:
            redis.exceptions.RedisError: If the Redis command fails.
        """
        key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
        try:
            data_str = json.dumps(student_data)
            await self.client.hset(key, student_id, data_str)
            logger.info(f"Added attendance record for student {student_id} in session {session_id}")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Add record failed for student {student_id} in session {session_id}: {e}")
            return False

    async def get_attendance(self, session_id: str) -> Optional[Dict[str, Dict]]:
        """
        Fetches all attendance records for the given session.

        Args:
            session_id (str): The identifier for the session.

        Returns:
            Dict[str, Dict]: A dictionary of student records, or an empty dict if none exist.

        Raises:
            redis.exceptions.RedisError: If the Redis command fails.
        """
        key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
        try:
            raw_data = await self.client.hgetall(key)
            if not raw_data:
                logger.warning(f"No attendance data found for session {session_id}")
                return {}

            parsed = {sid: json.loads(data) for sid, data in raw_data.items()}
            logger.info(f"Fetched attendance for session {session_id}, count: {len(parsed)}")
            return parsed
        except redis.exceptions.RedisError as e:
            logger.error(f"Get attendance failed for session {session_id}: {e}")
            return None

    async def export_attendance(self, session_id: str) -> Optional[Dict[str, Dict]]:
        """
        Exports attendance data for a session. (Alias for get_attendance).

        Args:
            session_id (str): The identifier for the session to export.

        Returns:
            Dict[str, Dict]: A dictionary of student records.

        Raises:
            redis.exceptions.RedisError: If the underlying get_attendance call fails.
        """
        logger.info(f"Exporting attendance for session {session_id}")
        return await self.get_attendance(session_id)
