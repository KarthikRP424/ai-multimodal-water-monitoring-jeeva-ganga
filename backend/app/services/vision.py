// backend/app/services/vision.py
"""YOLO inference service.

This module loads the YOLO model once at import time and provides a simple
`run_detection` function that can be called from the camera upload background
task. It is deliberately lightweight – it does not depend on any FastAPI
objects and can be used both synchronously (from a background task) and
asynchronously (if needed).

The implementation uses the `ultralytics` package, which provides the `YOLO`
class. The model path defaults to the `best.pt` file shipped with the project
(`backend/app/models/best.pt`). The environment variable ``YOLO_MODEL_PATH``
may be used to override the location.
"""

from __future__ import annotations

import os
import logging
from typing import List, Dict

# Set up a module‑level logger
logger = logging.getLogger(__name__)

# Load the model once. If the package or model file is missing we log an error
# and raise – the caller will catch and broadcast an "error" WS message.
try:
    from ultralytics import YOLO
except Exception as exc:  # pragma: no cover – import error handling
    logger.error("Failed to import ultralytics.YOLO: %s", exc)
    raise

# Resolve model path; default points inside the repository.
default_model_path = os.path.join(os.path.dirname(__file__), "..", "models", "best.pt")
model_path = os.getenv("YOLO_MODEL_PATH", default_model_path)

if not os.path.isfile(model_path):
    logger.error("YOLO model file not found at %s", model_path)
    raise FileNotFoundError(f"YOLO model not found: {model_path}")

# Load the model – this may take a few seconds, but it happens only once.
logger.info("Loading YOLO model from %s", model_path)
model = YOLO(model_path)


def _format_bbox(bbox: List[float]) -> Dict[str, float]:
    """Convert a YOLO bbox list `[x1, y1, x2, y2]` to a dict of coordinates.

    The frontend expects a simple `{x, y, w, h}` structure where ``x``/``y``
    represent the top‑left corner and ``w``/``h`` are width and height.
    """
    x1, y1, x2, y2 = bbox
    return {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}


def run_detection(image_path: str) -> List[Dict[str, object]]:
    """Run YOLO inference on ``image_path``.

    Returns a list of dictionaries, each containing:
    - ``class``: detected class name (str)
    - ``confidence``: confidence score between 0 and 1 (float)
    - ``bbox``: ``{x, y, w, h}`` dict in pixel coordinates (float)

    Any exception is propagated to the caller, which will broadcast an error.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    logger.info("Running YOLO detection on %s", image_path)
    # ``model`` returns a Results object; we take the first (and only) result.
    results = model(image_path)
    detections: List[Dict[str, object]] = []
    for r in results:
        # ``r.boxes`` holds detection boxes; ``r.names`` maps class IDs.
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls.item())
            class_name = r.names[cls_id]
            confidence = float(box.conf.item())
            bbox = _format_bbox(box.xyxy.tolist())
            detections.append({
                "class": class_name,
                "confidence": confidence,
                "bbox": bbox,
            })
    return detections
