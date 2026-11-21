# backend/app/services/alert_manager.py

"""Simple alert manager.

The ``notify`` function receives an ``event_type`` (e.g., "motion",
"human_detection", "animal_detection", "ultrasonic") and a payload dict.
It creates an ``Alert`` entry in the DB based on configurable rules.
All alerts are also broadcast to WebSocket clients via ``send_to_all``.
"""

import logging
from datetime import datetime
from typing import Dict

from .. import models, database
from ..broadcast import send_to_all

log = logging.getLogger(__name__)

# Configuration – in a real project these would be environment variables
WARNING_DISTANCE_CM = 150.0
CRITICAL_DISTANCE_CM = 80.0

def _create_alert(session, device_id: str, category: str, severity: str, description: str):
    alert = models.Alert(
        device_id=device_id,
        category=category,
        severity=severity,
        description=description,
        timestamp=datetime.utcnow(),
    )
    session.add(alert)
    session.commit()
    session.refresh(alert)
    # Broadcast alert
    import asyncio
    asyncio.create_task(send_to_all({"type": "alert", "payload": alert.dict()}))
    return alert

def notify(event_type: str, payload: Dict):
    """Entry point for all event‑driven alerts.

    ``event_type`` is a free‑form string used by routers.
    ``payload`` must contain at least ``device_id``.
    """
    device_id = payload.get("device_id")
    if not device_id:
        log.warning("Alert notification missing device_id: %s", payload)
        return None
    # Open a DB session for each call (short‑lived)
    with database.get_session() as session:
        if event_type == "motion":
            return _create_alert(
                session,
                device_id,
                category="motion",
                severity="info",
                description="PIR motion detected",
            )
        if event_type == "human_detection":
            confidence = payload.get("confidence", 0)
            severity = "warning" if confidence < 0.5 else "info"
            return _create_alert(
                session,
                device_id,
                category="human_detection",
                severity=severity,
                description=f"Human detected with confidence {confidence:.2f}",
            )
        if event_type == "animal_detection":
            obj = payload.get("class", "animal")
            confidence = payload.get("confidence", 0)
            return _create_alert(
                session,
                device_id,
                category="animal_detection",
                severity="info",
                description=f"{obj} detected (confidence {confidence:.2f})",
            )
        if event_type == "ultrasonic":
            distance = payload.get("distance_cm")
            if distance is None:
                return None
            if distance <= CRITICAL_DISTANCE_CM:
                severity = "critical"
                desc = f"Critical water level warning: {distance:.1f} cm"
            elif distance <= WARNING_DISTANCE_CM:
                severity = "warning"
                desc = f"Water level warning: {distance:.1f} cm"
            else:
                # No alert for normal readings
                return None
            return _create_alert(
                session,
                device_id,
                category="water_level",
                severity=severity,
                description=desc,
            )
        # Unknown event – ignore
        log.debug("No alert rule for event_type %s", event_type)
        return None
