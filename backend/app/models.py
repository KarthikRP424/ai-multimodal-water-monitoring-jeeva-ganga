# backend/app/models.py

from datetime import datetime
from sqlmodel import SQLModel, Field

class CameraEvent(SQLModel, table=True):
    __tablename__ = "camerapevent"


    id: int = Field(default=None, primary_key=True)
    device_id: str
    motion: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    image_path: str | None = None  # Path on server if stored

class PIRSensorEvent(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    device_id: str
    motion: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DetectionResult(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    camera_event_id: int = Field(foreign_key="camerapevent.id")
    object_class: str
    confidence: float
    bbox: str | None = None  # stored as JSON string if needed
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Alert(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    device_id: str
    category: str  # e.g., "motion", "human_detection", "water_warning"
    severity: str  # "info", "warning", "critical"
    description: str
    acknowledged: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UltrasonicReading(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    device_id: str
    distance_cm: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    warning: bool = False
    critical: bool = False

class DeviceHeartbeat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    device_id: str
    status: str  # e.g., "online", "offline"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
