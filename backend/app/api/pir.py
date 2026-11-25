# backend/app/api/pir.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session

from .. import models, database
from ..schemas import pir as pir_schema
from ..services import alert_manager
from ..broadcast import send_to_all

router = APIRouter()

@router.post("/", response_model=pir_schema.PIRSensorEventResponse)
def create_pir_event(
    event: pir_schema.PIRSensorEventCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(database.get_session),
):
    db_event = models.PIRSensorEvent(
        device_id=event.device_id,
        motion=event.motion,
        timestamp=event.timestamp or __import__('datetime').datetime.utcnow(),
    )
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    # Broadcast the event using FastAPI background tasks (avoids needing an active loop)
    background_tasks.add_task(send_to_all, {"type": "pir_event", "payload": db_event.model_dump()})
    # Generate alert if motion detected
    if event.motion:
        alert_manager.notify("motion", {"device_id": event.device_id, "motion": True}, background_tasks=background_tasks)
    return db_event
