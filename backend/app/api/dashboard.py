# backend/app/api/dashboard.py

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from datetime import datetime, timedelta

from .. import models, database

router = APIRouter()

@router.get("/", summary="Dashboard overview aggregation")
def get_overview(session: Session = Depends(database.get_session)):
    now = datetime.utcnow()
    # Total devices (distinct device_id across heartbeats)
    total_devices = session.exec(select(func.count(models.DeviceHeartbeat.device_id.distinct()))).one()
    # Online devices (status == "online" within last 2 minutes)
    recent = now - timedelta(minutes=2)
    online_sub = select(models.DeviceHeartbeat.device_id).where(
        models.DeviceHeartbeat.status == "online",
        models.DeviceHeartbeat.timestamp >= recent,
    ).group_by(models.DeviceHeartbeat.device_id)
    online_devices = session.exec(online_sub).count()

    # Recent human detections (last hour)
    human_det = select(func.count()).select_from(models.DetectionResult).where(
        models.DetectionResult.object_class.ilike("%person%") |
        models.DetectionResult.object_class.ilike("%human%"),
        models.DetectionResult.timestamp >= now - timedelta(hours=1),
    )
    human_count = session.exec(human_det).one()

    # Recent PIR motions (last hour)
    pir_motion = select(func.count()).where(
        models.PIRSensorEvent.motion == True,
        models.PIRSensorEvent.timestamp >= now - timedelta(hours=1),
    )
    pir_count = session.exec(pir_motion).one()

    # Latest ultrasonic reading
    latest_ultra = session.exec(
        select(models.UltrasonicReading).order_by(models.UltrasonicReading.timestamp.desc()).limit(1)
    ).first()
    latest_distance = latest_ultra.distance_cm if latest_ultra else None

    # Active alerts (unacknowledged)
    active_alerts = session.exec(
        select(func.count()).where(models.Alert.acknowledged == False)
    ).one()

    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "human_detections_last_hour": human_count,
        "pir_movements_last_hour": pir_count,
        "latest_ultrasonic_cm": latest_distance,
        "active_alerts": active_alerts,
    }
