import qrCode
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

class QRCodeRequest(BaseModel):
    data: str
    size: int = 200 

@router.post("/generate_qr_code", tags=["QR Code"])
def qr_code_endpoint(request: QRCodeRequest):
    """Generate a QR code from the provided data and size."""
    if not request.data:
        raise HTTPException(status_code=400, detail="Data for QR code cannot be empty.")
    
    try:
        qr_image = qrCode.generate_qr_code(request.data, request.size)
        image_stream = io.BytesIO()
        qr_image.save(image_stream, format='PNG')
        image_stream.seek(0)
        return StreamingResponse(image_stream, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))