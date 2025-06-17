from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import json
from . import qrRouters, attendRouters
from .middleware import global_exception_handler, add_process_time_header
from .config import app_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.is_running = True
    logging.info(json.dumps({
        "event": "startup",
        "message": "Application started"
    }))
    yield
    logging.info(json.dumps({
        "event": "shutdown",
        "message": "Application stopped"
    }))
    app.state.is_running = False

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

app.include_router(qrRouters.router, prefix="/qr", tags=["QR Code"])
app.include_router(attendRouters.router, prefix="/qr/attend", tags=["Attendance"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "API is alive!"}

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=5000,
        reload=True
    )
