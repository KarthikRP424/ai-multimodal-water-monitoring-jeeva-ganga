from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .. import models, database
from ..schemas import alerts as alerts_schema

router = APIRouter()

@router.get("/", response_model=list[alerts_schema.AlertResponse])
def list_alerts(skip: int = 0, limit: int = 100, session: Session = Depends(database.get_session)):
    alerts = session.exec(select(models.Alert).offset(skip).limit(limit)).all()
    return alerts

@router.post("/", response_model=alerts_schema.AlertResponse)
def create_alert_endpoint(alert: alerts_schema.AlertCreate, session: Session = Depends(database.get_session)):
    return create_alert(alert, session)

@router.patch("/{alert_id}", response_model=alerts_schema.AlertResponse)
def acknowledge_alert(alert_id: int, session: Session = Depends(database.get_session)):
    db_alert = session.get(models.Alert, alert_id)
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db_alert.acknowledged = True
    session.add(db_alert)
    session.commit()
    session.refresh(db_alert)
    return db_alert

def create_alert(alert: alerts_schema.AlertCreate, session: Session = Depends(database.get_session)):
    db_alert = models.Alert(
        device_id=alert.device_id,
        category=alert.category,
        severity=alert.severity,
        description=alert.description,
        timestamp=alert.timestamp or __import__('datetime').datetime.utcnow(),
    )
    session.add(db_alert)
    session.commit()
    session.refresh(db_alert)
    return db_alert