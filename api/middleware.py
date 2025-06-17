from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status
import logging
import json
import traceback
import time

async def global_exception_handler(request: Request, exc: Exception):
    log_payload = {
        "event": "unhandled_exception",
        "path": str(request.url),
        "error": str(exc),
        "trace": traceback.format_exc()
    }
    logging.error(json.dumps(log_payload))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "details": str(exc)
        }
    )

async def add_process_time_header(request: Request, call_next):
    """Middleware to add a custom header with the request processing time."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    log_payload = {
        "event": "request_completed",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time_ms": round(process_time * 1000, 2)
    }
    logging.info(json.dumps(log_payload))
    
    response.headers["X-Process-Time-Ms"] = str(log_payload["process_time_ms"])
    return response
