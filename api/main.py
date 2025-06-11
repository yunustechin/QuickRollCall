from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api.qrRouters as qrRouters
import uvicorn

app = FastAPI()

# Enable CORS for all origins, methods, and headers (development use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Enable CORS for all origins, methods, and headers (development use)
app.include_router(qrRouters.router, prefix="/qr", tags=["QR Code"])

# Health check or root endpoint
@app.get("/")
def root():
    if app.state.is_running:
        return {"message": "QR Code Generator API is running!"}
    else:
        return {"message": "QR Code Generator API is not running!"}
    
# Check if the application is running
if __name__ == "__main__":
    getattr(app.state,"is_running", False) 
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
