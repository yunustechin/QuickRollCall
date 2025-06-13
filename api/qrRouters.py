from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from generator.qrCode import QRCodeGenerator, UniqueIdGenerator
from db.redisClient import RedisClient
import io
import asyncio

router = APIRouter()
redis_client = RedisClient()

# NOTE: Replace with your actual domain and port in a production environment
BASE_URL = "http://127.0.0.1:5000" 

@router.get("/", tags=["QR Code"])
async def qr_base_page(request: Request):
    """
    Serves the main landing page (main.html) which provides entry points
    for both teachers and students.
    """
    templates = Jinja2Templates(directory="ui") 
    return templates.TemplateResponse("main.html", {"request": request})

@router.get("/teacher", tags=["QR Code"])
async def teacher_dashboard(request: Request):
    """
    This endpoint returns the HTML page that provides the user interface
    for generating new QR codes for attendance sessions.
    """
    templates = Jinja2Templates(directory="ui/teacher") 
    return templates.TemplateResponse("teacher.html", {"request": request})

def build_qr_stream() -> io.BytesIO:
    """
    Generates a unique session ID, stores it in Redis, and builds a QR code
    containing the direct URL to the attendance form.
    """
    id_generator = UniqueIdGenerator()
    session_id = id_generator.get_unique_id()

    if not redis_client.create_attendance_session(session_id=session_id):
        raise ValueError("Failed to create attendance session in Redis.")
    
    attendance_url = f"{BASE_URL}/qr/attend/{session_id}"
        
    qr_generator = QRCodeGenerator(data=attendance_url)
    qr_generator.generate_qr_code()

    qr_image = qr_generator.qr_code
    if qr_image is None:
        raise ValueError("QR code image could not be generated.")

    image_stream = io.BytesIO()
    qr_image.save(image_stream, format='PNG')
    image_stream.seek(0)
    return image_stream

@router.post("/generate-qr-code", tags=["QR Code"])
async def generate_qr_code() -> StreamingResponse:
    """"
    Endpoint to generate a QR code containing a unique URL for an attendance session.
    This creates the session in the backend.
    """
    try: 
        image_stream = await asyncio.to_thread(build_qr_stream)
        return StreamingResponse(image_stream, media_type="image/png")
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    