from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import logging
from pydantic import BaseModel
from db import RedisClient
from .config import rate_limit_settings
from .dependencies import get_redis_client


class StudentData(BaseModel):
    name: str
    surname: str
    school_no: str
    faculty: str
    section: str


router = APIRouter()
templates = Jinja2Templates(directory="ui/student")


async def validate_session_id(
    session_id: str,
    redis: RedisClient = Depends(get_redis_client)
) -> str:
    """Ensure session exists and is still open."""
    if not await redis.is_session_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This session is closed or expired."
        )
    return session_id


async def enforce_rate_limit(
    request: Request,
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Apply basic rate limit per client IP.
    Allow max 2 requests per 60 seconds.

    NOTE: Bypassed for local dev (127.0.0.1).
    """
    client_ip = request.client.host
    if client_ip == "127.0.0.1":
        return

    try:
        is_limited = await redis.check_rate_limit(
            client_id=client_ip,
            limit=rate_limit_settings.REQUESTS_LIMIT,
            window=rate_limit_settings.TIME_WINDOW
        )
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Try again later.",
                headers={"Retry-After": str(rate_limit_settings.TIME_WINDOW)}
            )
    except Exception as e:
        logging.error(f"Rate limit check failed for {client_ip}: {e}")


@router.get("/", tags=["Attendance"])
async def student_dashboard(request: Request):
    """Render QR scanner page for students."""
    return templates.TemplateResponse("student.html", {"request": request})


@router.get(
    "/{session_id}",
    dependencies=[Depends(enforce_rate_limit)],
    tags=["Attendance"]
)
async def show_attendance_form(
    request: Request,
    session_id: str = Depends(validate_session_id)
):
    """Show form if session is valid."""
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "session_id": session_id}
    )


@router.post(
    "/{session_id}",
    dependencies=[Depends(enforce_rate_limit)],
    tags=["Attendance"]
)
async def submit_attendance(
    student: StudentData,
    session_id: str = Depends(validate_session_id),
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Submit attendance data.
    Rejects duplicates.
    """
    if await redis.has_student_submitted(session_id, student.school_no):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance already submitted for this session."
        )

    success = await redis.add_student_record(
        session_id,
        student.school_no,
        student.model_dump()
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save attendance record."
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Attendance recorded successfully!"}
    ) 