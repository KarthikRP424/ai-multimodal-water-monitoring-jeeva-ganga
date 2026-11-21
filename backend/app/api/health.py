# backend/app/api/health.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """Simple health‑check endpoint used by monitoring tools.
    Returns a JSON payload with status ``ok`` when the service is running.
    """
    return {"status": "ok"}
