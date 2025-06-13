from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from . import qrRouters
from . import attendRouters
import uvicorn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.is_running = True
    yield 
    app.state.is_running = False

app = FastAPI(lifespan=lifespan)

app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Allow all CORS origins during development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qrRouters.router, prefix="/qr", tags=["QR Code"])
app.include_router(attendRouters.router, prefix="/qr/attend", tags=["Attendance"])

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Returns a success message if the API is up and running.
    """
    return {"status": "ok", "message": "QR Code Generator API is running!"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=5000, reload=True)
