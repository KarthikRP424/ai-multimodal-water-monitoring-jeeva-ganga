# backend/app/api/devices_status.py

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from .. import models, database

router = APIRouter()

@router.get("/", summary="Get summary status of all devices")
def get_devices_status(session: Session = Depends(database.get_session)):
    # Count distinct device IDs per type (camera, pir, ultrasonic)
    # For simplicity we infer type from prefixes in device_id (e.g., esp32_cam_, esp8266_ultrasonic_)
    stmt = select(models.DeviceHeartbeat.device_id, models.DeviceHeartbeat.status, models.DeviceHeartbeat.timestamp)
    rows = session.exec(stmt).all()
    # Aggregate latest status per device
    status_map = {}
    for row in rows:
        dev_id = row.device_id
        if dev_id not in status_map or row.timestamp > status_map[dev_id]["timestamp"]:
            status_map[dev_id] = {"status": row.status, "timestamp": row.timestamp}
    return status_map
