from fastapi import APIRouter, HTTPException, Request, Query, Depends, status
from fastapi.responses import StreamingResponse, Response
from fastapi.templating import Jinja2Templates
from enum import Enum
import io
import asyncio
import logging
from typing import Optional
from datetime import datetime
from .dependencies import get_redis_client
from generator.qrCode import QRCodeGenerator, UniqueIdGenerator
from generator.exportFile import ExportFile
from .config import app_settings

router = APIRouter()
templates = Jinja2Templates(directory="ui")

class ExportFormat(str, Enum):
    TXT = "txt"
    CSV = "csv"


def generate_qr_image_stream(data: str) -> Optional[io.BytesIO]:
    """Generate a QR code PNG stream from given data."""
    qr_generator = QRCodeGenerator(data=data)
    qr_generator.generate_qr_code()
    
    if qr_generator.qr_code is None:
        return None
    
    stream = io.BytesIO()
    qr_generator.qr_code.save(stream, format="PNG")
    stream.seek(0)
    return stream


async def build_qr_stream(redis: get_redis_client) -> tuple[str, io.BytesIO]:
    """Create a new session, generate its QR code as PNG stream."""
    session_id = UniqueIdGenerator().get_unique_id()

    if not await redis.create_attendance_session(session_id=session_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create session in Redis."
        )

    url = f"{app_settings.BASE_URL}/attend/{session_id}"
    stream = await asyncio.to_thread(generate_qr_image_stream, url)

    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate QR code image."
        )

    return session_id, stream


@router.get("/", tags=["QR Code"])
async def qr_base_page(request: Request):
    """Render landing page."""
    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/teacher", tags=["QR Code"])
async def teacher_dashboard(request: Request):
    """Render teacher dashboard for QR code generation."""
    return templates.TemplateResponse("teacher/teacher.html", {"request": request})


@router.post("/generate-qr-code", tags=["QR Code"])
async def generate_qr_code(redis: get_redis_client = Depends(get_redis_client)):
    """Generate QR code and return it with session ID in header."""
    try:
        session_id, stream = await build_qr_stream(redis)
        response = StreamingResponse(stream, media_type="image/png")
        response.headers["X-Session-ID"] = session_id
        response.headers["Access-Control-Expose-Headers"] = "X-Session-ID"
        return response
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error during QR generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the QR code."
        )
    

@router.post("/export/{session_id}", tags=["QR Code"])
async def export_session_data(
    session_id: str,
    format: ExportFormat = Query(...),
    redis: get_redis_client = Depends(get_redis_client)
):
    """Export session data and close the session."""
    attendance_data = await redis.export_attendance(session_id)
    if attendance_data is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch attendance data."
        )

    if not await redis.close_attendance_session(session_id):
        logging.warning(f"Session {session_id} could not be closed after export.")

    exporter = ExportFile(students_data=attendance_data)

    export_map = {
        ExportFormat.TXT: (exporter.generate_txt, "text/plain"),
        ExportFormat.CSV: (exporter.generate_csv, "text/csv"),
    }

    if format not in export_map:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid export format specified.")
    
    generate_method, media_type = export_map[format]
    content = generate_method()
    filename = f"rollcall_{datetime.now():%Y-%m-%d}.{format.value}"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
