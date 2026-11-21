# backend/app/schemas/detections.py

from pydantic import BaseModel, Field
from datetime import datetime

class DetectionResultCreate(BaseModel):
    camera_event_id: int = Field(..., description="FK to CameraEvent")
    object_class: str = Field(..., description="Detected class, e.g., person, dog")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0‑1")
    bbox: str | None = None  # JSON string for bounding box coordinates
    timestamp: datetime | None = None

class DetectionResultResponse(BaseModel):
    id: int
    camera_event_id: int
    object_class: str
    confidence: float
    bbox: str | None
    timestamp: datetime

    class Config:
        orm_mode = True
