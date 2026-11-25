from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CameraUploadCreate(BaseModel):
    device_id: str = Field(..., description="Unique identifier for the ESP32-CAM device")
    event_id: Optional[str] = Field(None, description="Client‑generated UUID; if omitted a UUID will be generated")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp of the capture")

class CameraUploadResponse(BaseModel):
    event_id: int = Field(..., description="Database primary key of the stored CameraEvent")
    status: str = Field("queued", description="Processing status – initially queued")
    device_id: str = Field(..., description="Device identifier from request")
    image_path: str = Field(..., description="Relative path of stored image file")
    event_id: int = Field(..., description="Database primary key of the stored CameraEvent")
    status: str = Field("queued", description="Processing status – initially queued")
