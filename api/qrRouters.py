from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import StreamingResponse, Response
from fastapi.templating import Jinja2Templates
from .dependencies import get_session_service
from .config import app_settings, access_token_settings
from pydantic import BaseModel
from .services import SessionService 
from .logger import log_error 
from enum import Enum

router = APIRouter()
templates = Jinja2Templates(directory="ui")

class ExportFormat(str, Enum):
    TXT = "txt"
    CSV = "csv"

class TokenRequest(BaseModel):
    session_id: str

@router.post("/api/request-attendance-token", tags=["Attendance Token"])
async def request_attendance_token(
    token_request: TokenRequest,
    service: SessionService = Depends(get_session_service) 
):
    """Generates and returns a one-time access token for a given session.

    Args:
        token_request (TokenRequest): The request body containing the session_id.
        service (SessionService): The dependency-injected session service.

    Returns:
        dict: A dictionary containing the generated one-time access token.
              Example: {"access_token": "your_generated_token"}
    """
    access_token = await service.get_one_time_token(token_request.session_id)
    return {"access_token": access_token}

@router.get("/", tags=["QR Code"])
async def qr_base_page(request: Request):
    """Renders the main landing page of the application.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        TemplateResponse: An HTML response rendering the main.html template.
    """
    return templates.TemplateResponse("main.html", {"request": request})

@router.get("/teacher", tags=["QR Code"])
async def teacher_dashboard(request: Request):
    """Renders the teacher's dashboard for initiating a new session.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        TemplateResponse: An HTML response rendering the teacher.html template.
    """
    return templates.TemplateResponse("teacher/teacher.html", {"request": request})

@router.post("/generate-qr-code", tags=["QR Code"])
async def generate_qr_code(
    request: Request, 
    service: SessionService = Depends(get_session_service) 
):
    """Creates a new attendance session and returns a QR code image stream.

    Args:
        request (Request): The incoming FastAPI request object.
        service (SessionService): The dependency-injected session service.

    Returns:
        StreamingResponse: A response streaming the generated QR code as a PNG image.
                           The custom 'X-Session-ID' header contains the new session ID.

    Raises:
        Exception: Propagates any exception that occurs during the QR code
                   session creation and logs the error.
    """
    try:
        base_url = str(request.base_url)
        session_id, stream = await service.create_qr_session(base_url)
        
        response = StreamingResponse(stream, media_type="image/png")
        response.headers["X-Session-ID"] = session_id
        response.headers["Access-Control-Expose-Headers"] = "X-Session-ID"
        return response
    except Exception as e:
        log_error("qr_generation_endpoint_error", e, {})
        raise e

@router.post("/export/{session_id}", tags=["QR Code"])
async def export_session_data(
    session_id: str,
    format: ExportFormat = Query(..., description="The desired file format for the export."),
    service: SessionService = Depends(get_session_service) 
):
    """Exports attendance data for a given session and then closes it.

    Args:
        session_id (str): The unique identifier for the session to be exported.
        format (ExportFormat): The target format for the data export (txt or csv).
        service (SessionService): The dependency-injected session service.

    Returns:
        Response: A response containing the exported data as a file attachment,
                  with appropriate media type and 'Content-Disposition' headers.
    """
    content, media_type, filename = await service.finalize_session_export(
        session_id, format.value
    )
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )