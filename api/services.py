from db import RedisClient
from utils.generate import QRCodeGenerator, UniqueIdGenerator
from utils.export import StudentDataExporter
from .config import access_token_settings
from .exceptions import APIServiceError, SessionNotFoundOrClosedError
from .logger import log_error, log_info
import io
from typing import Tuple
import asyncio

class SessionService:
    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.id_generator = UniqueIdGenerator()

    async def create_qr_session(self, base_url: str) -> Tuple[str, io.BytesIO]:
        """Create a new attendance session and generate a QR code image."""
        session_id = self.id_generator.generate()

        if not await self.redis.create_session(session_id=session_id):
            log_error("redis_session_creation_failed", Exception("Failed to create session"),{"session_id": session_id})
            raise APIServiceError("Could not create a new session.")
        
        url_to_encode = f"{base_url}qr/attend/{session_id}"
        stream = await asyncio.to_thread(SessionService.generate_qr_image, url_to_encode)

        if stream is None:
            log_error("qr_generation_failed", Exception("Failed to generate QR image"), {"session_id": session_id})
            raise APIServiceError("Failed to generate QR code image.")
        
        log_info("session_created", {"session_id": session_id})
        return session_id, stream

    async def get_one_time_token(self, session_id: str) -> str:
        """Generates and stores a one-time access token for a session."""
        if not await self.redis.is_session_valid(session_id):
            raise SessionNotFoundOrClosedError(session_id)
            
        access_token = self.id_generator.generate()
        success = await self.redis.set_access_token(
            token=access_token,
            session_id=session_id,
            expire_seconds=access_token_settings.EXPIRE_SECONDS
        )

        if not success:
            log_error("redis_token_set_failed", Exception("Failed to set token"), {"session_id": session_id})
            raise APIServiceError("Could not generate access token.")
        
        log_info("access_token_generated", {"session_id": session_id})
        return access_token

    async def finalize_session_export(self, session_id: str, format: str) -> Tuple[str, str, str]:
        """Exports attendance data, closes the session, and returns file content."""
        attendance_data = await self.redis.export_attendance(session_id)
        if attendance_data is None:
            raise APIServiceError("Could not fetch attendance data.")

        if not await self.redis.close_session(session_id):
            log_info("session_close_failed_after_export", {"session_id": session_id})

        exporter = StudentDataExporter(students_data=attendance_data)
        exporters = {
            "txt": ("text/plain", exporter.generate_txt),
            "csv": ("text/csv", exporter.generate_csv)
        }

        try:
            media_type, generator = exporters[format]
            content = generator()
        except KeyError:
            raise APIServiceError("Invalid export format specified", status_code=400)
            
        log_info("session_exported", {"session_id": session_id, "format": format})
        return content, media_type, f"rollcall_{session_id}.{format}"
    
    @staticmethod
    def generate_qr_image(url_to_encode: str) -> io.BytesIO:
            """Generate QR code image for the attendance URL."""
            qr_gen = QRCodeGenerator()
            qr_image = qr_gen.generate(data=url_to_encode)
            if qr_image is None:
                return None
            stream = io.BytesIO()
            qr_gen.save(qr_image, stream, format="PNG")
            stream.seek(0)
            return stream
        
        