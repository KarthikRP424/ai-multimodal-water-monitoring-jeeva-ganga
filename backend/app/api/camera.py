import asyncio
import asyncio
import os
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session
from datetime import datetime

from .. import models, database
from ..schemas import camera as camera_schema
from ..broadcast import send_to_all
from ..services import vision

router = APIRouter()

# Helper to generate a unique event_id if client does not provide one
def _generate_event_id() -> str:
    return str(uuid.uuid4())

@router.post("/upload", response_model=camera_schema.CameraUploadResponse)
async def upload_image(
    device_id: str = Form(...),
    event_id: str = Form(None),
    timestamp: datetime = Form(None),
    file: UploadFile = File(...),
    session: Session = Depends(database.get_session),
):
    """Accept a JPEG image from an ESP32‑CAM.
    Stores the raw file, creates a CameraEvent record and enqueues YOLO processing.
    """
    # Basic validation
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")
    # Use provided timestamp or now
    ts = timestamp or datetime.utcnow()
    # Ensure event_id is present
    ev_id = event_id or _generate_event_id()

    # Build a safe filename
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{ev_id}{ext}"
    upload_path = os.path.join(os.getenv("UPLOAD_DIR", "uploads"), filename)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)

    # Write the file to disk
    try:
        with open(upload_path, "wb") as out_file:
            content = await file.read()
            out_file.write(content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to write image file") from exc

    # Create DB entry (image_path stored relative to UPLOAD_DIR)
    db_event = models.CameraEvent(
        device_id=device_id,
        motion=False,  # motion flag is not used here; PIR is separate
        timestamp=ts,
        image_path=filename,
    )
    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    # Broadcast camera event with image URL
    asyncio.create_task(
        send_to_all({
            "type": "camera_event",
            "payload": {
                "event_id": db_event.id,
                "image_url": f"/uploads/{filename}",
                "timestamp": ts.isoformat(),
            },
        })
    )

    asyncio.create_task(
        process_camera_image(db_event.id, upload_path)
    )

    return camera_schema.CameraUploadResponse(event_id=db_event.id, status="queued", device_id=device_id, image_path=filename)

# Background processing – placed in this file to avoid circular imports
async def process_camera_image(event_id: int, image_path: str):
    """Run YOLO on the saved image, store results, and broadcast via WS."""
    try:
        detections = vision.run_detection(image_path)
        # Store each detection
        with database.get_session() as sess:
            # Store each detection
            for det in detections:
                db_det = models.DetectionResult(
                    camera_event_id=event_id,
                    object_class=det["class"],
                    confidence=det["confidence"],
                    bbox=det["bbox"],
                )
                sess.add(db_det)
            sess.commit()
            # Human detection alert
            human_detected = any(
                det["class"].lower() == "person" and det["confidence"] >= 0.6
                for det in detections
            )
            if human_detected:
                # Retrieve the camera event to get device_id
                cam_event = sess.get(models.CameraEvent, event_id)
                alert = models.Alert(
                    device_id=cam_event.device_id,
                    category="human_detection",
                    severity="info",
                    description="Human detected in camera feed",
                )
                sess.add(alert)
                sess.commit()
        # Broadcast result to front‑end
        await send_to_all({
            "type": "detection",
            "payload": {
                "event_id": event_id,
                "detections": detections,
            },
        })
    except Exception as exc:
        # On error we still broadcast an error payload so UI can show it
        await send_to_all({
            "type": "error",
            "payload": {
                "event_id": event_id,
                "reason": str(exc),
            },
        })

# Optional: list recent camera events for UI consumption
@router.get("/events", response_model=list[camera_schema.CameraUploadResponse])
def list_events(limit: int = 50, session: Session = Depends(database.get_session)):
    events = session.exec(
        models.CameraEvent.select().order_by(models.CameraEvent.timestamp.desc()).limit(limit)
    ).all()
    return [camera_schema.CameraUploadResponse(event_id=e.id, status="stored") for e in events]


# (Removed duplicate definitions that overwrote the enhanced endpoint implementations)
