# backend/app/ai/inference.py

"""YOLO inference helper.

- Tries to import the Ultralytics YOLO model (`from ultralytics import YOLO`).
- If the weight file `models/best.pt` exists, it loads the model and runs inference.
- If the library or the weight file is unavailable, the function falls back to an empty list
  and logs a warning. This satisfies the *safe fallback* requirement.

The function returns a list of dicts with keys:
  - ``class`` (str): detected object class name
  - ``confidence`` (float): confidence 0‑1
  - ``bbox`` (optional dict): ``{"x":...,"y":...,"w":...,"h":...}``
"""

import logging
from pathlib import Path
from typing import List, Dict

log = logging.getLogger(__name__)

# Attempt to import YOLO – optional dependency
try:
    from ultralytics import YOLO  # type: ignore
except Exception as e:  # pragma: no cover
    YOLO = None  # type: ignore
    log.warning("Ultralytics YOLO not installed: %s", e)

# Path to model weights (project root /models/best.pt)
_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "best.pt"

def _load_model():
    """Load YOLO model if available, otherwise return ``None``.
    The function is called lazily on first inference.
    """
    if YOLO is None:
        return None
    if not _MODEL_PATH.is_file():
        log.warning("YOLO weight file not found at %s – inference will be disabled", _MODEL_PATH)
        return None
    try:
        model = YOLO(str(_MODEL_PATH))
        return model
    except Exception as e:  # pragma: no cover
        log.error("Failed to load YOLO model: %s", e)
        return None

# Keep a singleton model instance
_model_instance = None

def process_image(image_path: str) -> List[Dict]:
    """Run YOLO on ``image_path`` and return detection list.

    Returns ``[]`` if model is unavailable.
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = _load_model()
    if _model_instance is None:
        # Safe fallback – no detections
        return []
    try:
        results = _model_instance(image_path)
        detections = []
        for r in results:
            boxes = r.boxes
            for b in boxes:
                cls = r.names[int(b.cls)] if hasattr(r, "names") else "unknown"
                conf = float(b.conf)
                xywh = b.xywh.tolist()[0] if hasattr(b, "xywh") else None
                bbox = None
                if xywh:
                    bbox = {"x": xywh[0], "y": xywh[1], "w": xywh[2], "h": xywh[3]}
                detections.append({"class": cls, "confidence": conf, "bbox": bbox})
        return detections
    except Exception as e:  # pragma: no cover
        log.error("YOLO inference failed: %s", e)
        return []
