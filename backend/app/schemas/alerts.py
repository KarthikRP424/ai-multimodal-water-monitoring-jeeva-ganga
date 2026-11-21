# backend/app/schemas/alerts.py

from pydantic import BaseModel, Field
from datetime import datetime

class AlertCreate(BaseModel):
    device_id: str = Field(..., description="Device that generated the alert")
    category: str = Field(..., description="Category, e.g., motion, human_detection, water_warning")
    severity: str = Field(..., description="info, warning, critical")
    description: str = Field(..., description="Human‑readable description")
    timestamp: datetime | None = None

class AlertResponse(BaseModel):
    id: int
    device_id: str
    category: str
    severity: str
    description: str
    acknowledged: bool
    timestamp: datetime

    class Config:
        orm_mode = True
