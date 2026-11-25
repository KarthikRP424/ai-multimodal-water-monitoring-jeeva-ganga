# backend/app/schemas/pir.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PIRSensorEventCreate(BaseModel):
    device_id: str = Field(..., description="Unique identifier for ESP32‑CAM device")
    motion: bool = Field(..., description="True when PIR detects motion")
    timestamp: datetime | None = None

class PIRSensorEventResponse(BaseModel):
    id: int
    device_id: str
    motion: bool
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
