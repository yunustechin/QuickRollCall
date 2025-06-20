from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi import status
from .logger import log_info, log_error
import traceback
import time

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """ A global exception handler to catch any unhandled exceptions."""
    log_error(
        event="unhandled_exception",
        err=exc,
        details={
            "path": str(request.url),
            "traceback": traceback.format_exc()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )

async def add_process_time_header(request: Request, call_next):
    """Middleware to add a custom header with the request processing time."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    log_info(
        event="request_completed",
        details={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": process_time
        }
    )
    
    response.headers["X-Process-Time-Ms"] = str(["process_time_ms"])
    return response
