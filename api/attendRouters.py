from fastapi import APIRouter, Depends, Request, status, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from db import RedisClient
from .config import app_settings, rate_limit_settings
from .dependencies import get_redis_client
from .exceptions import TokenInvalidError, TokenMismatchError, SessionNotFoundOrClosedError, DuplicateAttendanceError, APIServiceError
from .logger import log_error, log_info
import logging

class StudentData(BaseModel):
    name: str
    surname: str
    school_no: str
    faculty: str
    section: str

router = APIRouter()
templates = Jinja2Templates(directory="ui/student")

async def validate_one_time_token(
    session_id: str, 
    token: str = Query(...), 
    redis: RedisClient = Depends(get_redis_client)
) -> str:
    """
    Validates a one-time use token against the session ID.

    This function consumes a one-time token to ensure it is valid and
    corresponds to the given session ID. It is used to prevent unauthorized
    access to the attendance form.

    Args:
        session_id (str): The identifier of the current session.
        token (str): The one-time token to be validated.
        redis (RedisClient): The Redis client dependency for database operations.

    Returns:
        str: The session ID if the token is valid and matches.

    Raises:
        TokenInvalidError: If the token does not exist or has already been used.
        TokenMismatchError: If the token is valid but does not match the session ID.
    """
    retrieved_session_id = await redis.consume_access_token(token)
    if not retrieved_session_id:
        raise TokenInvalidError()
    if retrieved_session_id != session_id:
        raise TokenMismatchError()
    
    log_info("token_validated", {"session_id": session_id})
    return session_id

async def validate_session_id(
    session_id: str,
    redis: RedisClient = Depends(get_redis_client)
) -> str:
    """
    Ensures that a session exists and is currently open for attendance.

    Args:
        session_id (str): The ID of the session to validate.
        redis (RedisClient): The Redis client for checking the session's status.

    Returns:
        str: The session ID if it is valid and open.

    Raises:
        SessionNotFoundOrClosedError: If the session does not exist or is no longer active.
    """
    if not await redis.is_session_valid(session_id):
        raise SessionNotFoundOrClosedError(session_id)
    return session_id

async def enforce_rate_limit(
    request: Request,
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Applies a basic rate limit based on the client's IP address.

    This function restricts the number of requests from a single IP to prevent
    abuse. The rate limit is bypassed for local development environments.

    Args:
        request (Request): The incoming request object, used to identify the client's IP.
        redis (RedisClient): The Redis client for tracking request counts.

    Raises:
        HTTPException: If the client has exceeded the defined request limit.
    """
    client_ip = request.client.host
    # Bypass rate limiting for local development
    if client_ip == app_settings.CLIENT_IP:
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
    """
    Renders the main student page, which includes the QR code scanner.

    Args:
        request (Request): The incoming request object.

    Returns:
        TemplateResponse: The HTML page for the student dashboard.
    """
    return templates.TemplateResponse("student.html", {"request": request})

@router.get("/{session_id}", dependencies=[Depends(enforce_rate_limit)])
async def show_attendance_form(
    request: Request,
    validated_session_id: str = Depends(validate_one_time_token)
):
    """
    Displays the attendance form if the session and token are valid.

    Args:
        request (Request): The incoming request object.
        validated_session_id (str): The session ID, validated by `validate_one_time_token`.

    Returns:
        TemplateResponse: The HTML form for submitting attendance.
    """
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "session_id": validated_session_id}
    )

@router.post("/{session_id}", dependencies=[Depends(enforce_rate_limit)])
async def submit_attendance(
    student: StudentData,
    session_id: str = Depends(validate_session_id),
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Handles the submission of the attendance form.

    This endpoint validates the session and checks for duplicate submissions
    before recording the student's attendance.

    Args:
        student (StudentData): The attendance data submitted by the student.
        session_id (str): The session ID, validated to ensure the session is active.
        redis (RedisClient): The Redis client for database interactions.

    Returns:
        JSONResponse: A success message if the attendance is recorded.

    Raises:
        DuplicateAttendanceError: If the student has already submitted attendance for this session.
        APIServiceError: If the student record fails to be saved in the database.
    """
    if await redis.has_student_submitted(session_id, student.school_no):
        raise DuplicateAttendanceError()

    success = await redis.add_student_record(
        session_id,
        student.school_no,
        student.model_dump()
    )
    if not success:
        log_error("redis_record_add_failed", Exception("Failed to add student record"), {
            "session_id": session_id,
            "student_no": student.school_no
        })
        raise APIServiceError("Could not save attendance record.")
    
    log_info("attendance_submitted", {"session_id": session_id, "student_no": student.school_no})
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Attendance recorded successfully!"}
    )