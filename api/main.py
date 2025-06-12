from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from . import qrRouters

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.is_running = True
    yield 
    app.state.is_running = False

app = FastAPI(lifespan=lifespan)

# Mount the main directory for all frontend static assets
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Allow all CORS origins during development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register QR Code related routes under the /qr prefix
app.include_router(qrRouters.router, prefix="/qr", tags=["QR Code"])

# Health check endpoint for monitoring API status
@app.get("/")
def root():
    if not getattr(app.state, "is_running", False):
        return {"message": "QR Code Generator API is not running!"}
    return {"message": "QR Code Generator API is running!"}


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=5000, reload=True)
