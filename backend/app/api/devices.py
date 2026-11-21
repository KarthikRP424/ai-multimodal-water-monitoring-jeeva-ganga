# backend/app/api/devices.py

from fastapi import APIRouter, Depends
from sqlmodel import Session

from .. import models, database
from ..schemas import devices as device_schema

router = APIRouter()

@router.post("/heartbeat", response_model=device_schema.DeviceHeartbeatResponse)
def send_heartbeat(heartbeat: device_schema.DeviceHeartbeatCreate, session: Session = Depends(database.get_session)):
    db_hb = models.DeviceHeartbeat(
        device_id=heartbeat.device_id,
        status=heartbeat.status,
        timestamp=heartbeat.timestamp,
    )
    session.add(db_hb)
    session.commit()
    session.refresh(db_hb)
    return db_hb
