from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from db.redisClient import RedisClient
from pydantic import BaseModel
import logging

class StudentData(BaseModel):
    name: str
    surname: str
    school_no: str
    faculty: str
    section: str

router = APIRouter()
redis_client = RedisClient()
templates = Jinja2Templates(directory="ui/student")

async def rate_limit_dependency(request: Request):
    """
    Prevents abuse by limiting requests from a single IP address.
    Allows 2 requests per 60 seconds.

    NOTE: This check is bypassed for local development requests (from 127.0.0.1).
    """
    if request.client.host == "127.0.0.1":
        return
    
    if not redis_client.client:
        logging.warning("Redis client not available for rate limiting.")
        return

    client_id = request.client.host
    rate_limit_key = f"rate_limit:{client_id}"
    
    REQUESTS_LIMIT = 2
    TIME_WINDOW = 60 # seconds

    try:
        pipe = redis_client.client.pipeline()
        pipe.incr(rate_limit_key)
        pipe.expire(rate_limit_key, TIME_WINDOW, nx=True)
        
        results = pipe.execute()
        requests_count = results[0]

        if requests_count > REQUESTS_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again in a minute.",
                headers={"Retry-After": str(TIME_WINDOW)},
            )
    except Exception as e:
        logging.error(f"Could not perform rate limiting for {client_id}: {e}")
        pass

@router.get("/", tags=["Attendance"])
async def student_dashboard(request: Request):
    """Endpoint to retrieve the student QR scanner page."""
    try:
        return templates.TemplateResponse("student.html", {"request": request})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found.")

@router.get("/{session_id}", dependencies=[Depends(rate_limit_dependency)], tags=["Attendance"])
async def student_form(request: Request, session_id: str):
    """
    Validates the session_id from the QR code URL.
    If valid and session is open, displays the attendance form.
    """
    if not redis_client.is_session_valid(session_id):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="This attendance session is closed or has expired.")

    return templates.TemplateResponse("form.html", {"request": request, "session_id": session_id})

@router.post("/{session_id}", dependencies=[Depends(rate_limit_dependency)], tags=["Attendance"])
async def submit_attendance(session_id: str, student_data: StudentData):
    """
    Handles student attendance form submission.
    Validates the session and prevents duplicate submissions.
    """
    if not redis_client.is_session_valid(session_id):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Attendance session is closed or has expired.")

    if redis_client.has_student_submitted(session_id, student_data.school_no):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already submitted your attendance for this session.")

    if not redis_client.add_student_record(session_id, student_data.school_no, student_data.dict()):
        raise HTTPException(status_code=500, detail="Failed to save attendance record.")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Attendance submitted successfully!"}
    )