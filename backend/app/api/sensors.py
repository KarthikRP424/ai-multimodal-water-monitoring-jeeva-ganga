"""Ultrasonic sensor API endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel import Session
from datetime import datetime

from .. import models, database
from ..schemas import sensors as sensor_schema
from ..services import alert_manager
from ..broadcast import send_to_all
import asyncio

router = APIRouter()

@router.post(
    "/ultrasonic",
    response_model=sensor_schema.UltrasonicReadingResponse,
)
def create_ultrasonic_reading(
    reading: sensor_schema.UltrasonicReadingCreate,
    session: Session = Depends(database.get_session),
):
    """Create a new ultrasonic reading, broadcast it and trigger alerts."""
    db_reading = models.UltrasonicReading(
        device_id=reading.device_id,
        distance_cm=reading.distance_cm,
        timestamp=reading.timestamp or datetime.utcnow(),
        warning=reading.warning or False,
        critical=reading.critical or False,
    )
    session.add(db_reading)
    session.commit()
    session.refresh(db_reading)
    # Broadcast to WebSocket clients
    asyncio.create_task(
        send_to_all({"type": "ultrasonic_reading", "payload": db_reading.dict()})
    )
    # Alert manager handles water‑level thresholds
    alert_manager.notify(
        "ultrasonic",
        {"device_id": reading.device_id, "distance_cm": reading.distance_cm},
    )
    return db_reading
