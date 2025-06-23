from redis.asyncio import Redis
import redis.exceptions
import json
import logging
from typing import Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

class AttendanceManager:
    _ATTENDANCE_KEY_PREFIX = "attendance:{}"

    def __init__(self, client: Redis):
        self.client = client

    def _has_submitted_sync(self, session_id: str, student_id: str) -> bool:
        """Executes the blocking Redis command to check for a student's submission."""
        key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
        return self.client.hexists(key, student_id)

    def _add_record_sync(self, session_id: str, student_id: str, student_data: Dict):
        """Executes the blocking Redis command to add a student's attendance record."""
        key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
        data_str = json.dumps(student_data)
        self.client.hset(key, student_id, data_str)

    def _get_attendance_sync(self, session_id: str) -> Optional[Dict[str, Dict]]:
        """Executes the blocking Redis command to fetch all attendance records for a session."""
        key = self._ATTENDANCE_KEY_PREFIX.format(session_id)
        raw_data = self.client.hgetall(key)
        if not raw_data:
            return {}
        return {sid: json.loads(data) for sid, data in raw_data.items()}
    
    async def has_submitted(self, session_id: str, student_id: str) -> bool:
        """
        Checks if a student has already submitted attendance for the given session.
        This operation is executed in a separate thread to avoid blocking.

        Args:
            session_id (str): The identifier for the session.
            student_id (str): The identifier for the student.

        Returns:
            bool: True if the student has submitted, otherwise False.
        """
        try:
            return await asyncio.to_thread(self._has_submitted_sync, session_id, student_id)
        except redis.exceptions.RedisError as e:
            logger.error(f"Check submission failed for student {student_id} in session {session_id}: {e}")
            return False

    async def add_record(self, session_id: str, student_id: str, student_data: Dict) -> bool:
        """
        Adds or updates a student’s attendance record for a session.
        This operation is executed in a separate thread to avoid blocking.

        Args:
            session_id (str): The identifier for the session.
            student_id (str): The identifier for the student (to be used as the hash field).
            student_data (Dict): The student's data to store as a JSON string.

        Returns:
            bool: True if the record was added successfully, otherwise False.
        """
        try:
            await asyncio.to_thread(self._add_record_sync, session_id, student_id, student_data)
            logger.info(f"Added attendance record for student {student_id} in session {session_id}")
            return True
        except (redis.exceptions.RedisError, TypeError) as e:
            logger.error(f"Add record failed for student {student_id} in session {session_id}: {e}")
            return False

    async def export_attendance(self, session_id: str) -> Optional[Dict[str, Dict]]:
        """
        Exports attendance data for a session by fetching all records.
        This operation is executed in a separate thread to avoid blocking.

        Args:
            session_id (str): The identifier for the session to export.

        Returns:
            A dictionary of student records, or None if an error occurs.
        """
        logger.info(f"Exporting attendance for session {session_id}")
        try:
            attendance_data = await asyncio.to_thread(self._get_attendance_sync, session_id)
            if not attendance_data:
                logger.warning(f"No attendance data found for session {session_id}")
            else:
                logger.info(f"Fetched attendance for session {session_id}, count: {len(attendance_data)}")
            return attendance_data
        except redis.exceptions.RedisError as e:
            logger.error(f"Export attendance failed for session {session_id}: {e}")
            return None
