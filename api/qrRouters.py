from core.attendance.qrCode import QRCodeGenerator,UniqueIdGenerator
import io
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

def build_qr_stream():
    """
    Builds a QR code image stream using a generated unique ID.

    Returns:
        BytesIO: In-memory PNG image stream of the generated QR code.
    """
    id_generator = UniqueIdGenerator()
    unique_id = id_generator.get_unique_id()
        
    qr_generator = QRCodeGenerator(data=unique_id)
    qr_generator.generate_qr_code()

    qr_image = qr_generator.qr_code
    if qr_image is None:
        raise ValueError("QR code image could not be generated.")

    image_stream = io.BytesIO()
    qr_image.save(image_stream, format='PNG')
    image_stream.seek(0)
    return image_stream

@router.get("/attend",tags=["Student Dashboard"])
async def student_dashboard():
    """
    Endpoint to retrieve the student dashboard.

    Returns:
        dict: A dictionary containing the student dashboard data.
    
    Raises:
        HTTP404: If the template file is not found.
        HTTP500: For unexpected server errors.
    """
    try:
        templates = Jinja2Templates(directory="ui/student")
        return templates.TemplateResponse("student.html", {"request": {}})
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-qr-code", tags=["QR Code"])
async def generate_qr_code():
    """"
    Endpoint to generate a QR code with a unique ID.

    Returns:
        StreamingResponse: A streaming response containing the QR code image.
    
    Raises:
        HTTP400: If the QR code generation fails.
        HTTP500: For unexpected server errors.
    """
    try: 
        image_stream = await asyncio.to_thread(build_qr_stream)
        return StreamingResponse(image_stream, media_type="image/png")
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
