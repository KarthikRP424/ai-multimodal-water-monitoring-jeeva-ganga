# backend/app/schemas/devices.py

from pydantic import BaseModel, Field
from datetime import datetime

class DeviceHeartbeatCreate(BaseModel):
    device_id: str = Field(..., description="Unique identifier for the device")
    status: str = Field(..., description="Device status, e.g., 'online' or 'offline'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DeviceHeartbeatResponse(BaseModel):
    id: int
    device_id: str
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True
