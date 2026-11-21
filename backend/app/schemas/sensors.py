# backend/app/schemas/sensors.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UltrasonicReadingCreate(BaseModel):
    device_id: str = Field(..., description="Unique identifier for ESP8266 device")
    distance_cm: float = Field(..., ge=0, description="Measured distance in centimeters")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    warning: Optional[bool] = False
    critical: Optional[bool] = False

class UltrasonicReadingResponse(BaseModel):
    id: int
    device_id: str
    distance_cm: float
    timestamp: datetime
    warning: bool
    critical: bool

    class Config:
        orm_mode = True
