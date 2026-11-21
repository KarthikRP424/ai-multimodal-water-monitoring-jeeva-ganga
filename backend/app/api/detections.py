# backend/app/api/detections.py

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List

from .. import models, database
from ..schemas import detections as detections_schema

router = APIRouter()

@router.get("/", response_model=List[detections_schema.DetectionResultResponse])
def get_detections(skip: int = 0, limit: int = 100, session: Session = Depends(database.get_session)):
    stmt = select(models.DetectionResult).offset(skip).limit(limit)
    results = session.exec(stmt).all()
    return results
