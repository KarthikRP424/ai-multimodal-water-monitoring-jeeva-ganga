# backend/app/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api import camera, sensors, devices, pir, alerts, devices_status, dashboard, detections, ws, health


app = FastAPI(title="JEEVA GANGA Backend", version="0.1.0")

# Import database (which imports models) and initialise tables before the app starts
from . import database
# Database tables will be initialized on startup

@app.on_event("startup")
async def on_startup():
    # Initialise database tables
    from . import database
    database.init_db()

# Allow frontend (localhost:5173) to call backend
import os

# Allow frontend (localhost:5173) to call backend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # configurable via environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the uploads directory exists at startup
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Include routers

app.include_router(camera.router, prefix="/api/camera", tags=["camera"])
app.include_router(pir.router, prefix="/api/sensors/pir", tags=["pir"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(devices_status.router, prefix="/api/devices/status", tags=["devices_status"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(detections.router, prefix="/api/detections", tags=["detections"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

app.include_router(health.router, prefix="/api", tags=["health"])

# Mount static frontend files
import os
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

import httpx
from fastapi.responses import StreamingResponse

@app.get("/camera-proxy")
async def camera_proxy():
    """Proxy the ESP‑CAM stream so clients that cannot reach the camera directly can still see it.
    The PC runs the FastAPI server, fetches the MJPEG stream from the ESP‑CAM, and streams it back to the browser.
    """
    async def stream_generator():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", "http://192.168.163.69/") as resp:
                async for chunk in resp.aiter_bytes():
                    yield chunk
    return StreamingResponse(stream_generator(), media_type="multipart/x-mixed-replace;boundary=frame")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
