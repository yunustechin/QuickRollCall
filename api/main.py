from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from db import RedisClient
import redis.exceptions
import uvicorn
import redis
from . import qrRouters, attendRouters
from .middleware import global_exception_handler, add_process_time_header
from .config import app_settings
from .logger import setup_logging, log_info, log_error
from .dependencies import get_redis_client 


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    
    This context manager is used by FastAPI to execute code before the
    application starts receiving requests and right after it finishes.
    """
    setup_logging()
    log_info("startup", details={"message": "Application started"})
    yield
    log_info("shutdown", details={"message": "Application stopped"})

app = FastAPI(
    title="QR Code Generator API",
    description="Generate QR codes and manage attendance sessions.",
    version="1.0.0",
    lifespan=lifespan
)

app.middleware("http")(add_process_time_header)
app.add_exception_handler(Exception, global_exception_handler)
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # FIXME: tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root_redirect():
    return RedirectResponse(url="/qr")

app.include_router(qrRouters.router, prefix="/qr", tags=["QR Code"])
app.include_router(attendRouters.router, prefix="/qr/attend", tags=["Attendance"])

@app.get("/live",tags=["Health"])
def liveness_check():
    return {"status": "ok"}

@app.get("/ready", tags=["Health"])
async def readiness_check(redis_client: RedisClient = Depends(get_redis_client)):
    try: 
        if not await redis_client.ping():
            raise ConnectionError("Redis server did not respond to PING command.")
        
        return {"status": "ok", "dependencies": {"redis": "ready"}}

    except (redis.exceptions.ConnectionError, ConnectionRefusedError, redis.exceptions.TimeoutError) as e:
        log_error("readiness_check_failed", e, {"dependency": "redis"})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "dependencies": {"redis": "unavailable"}}
        )
    
    except Exception as e:
        log_error("readiness_check_failed_unexpected", e, {"dependency": "redis"})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "An unexpected error occurred during readiness check."}
        )

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=app_settings.CLIENT_IP,
        port=app_settings.PORT,
        reload=True
    )
