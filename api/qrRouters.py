from core.attendance.qrCode import QRCodeGenerator,UniqueIdGenerator
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/generate-qr-code", tags=["QR Code"])
def qr_code_endpoint():
    """Generate a QR code from the provided data and size."""
    
    try:
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
        
        return StreamingResponse(image_stream, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))