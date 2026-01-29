
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.JobResponse])
def get_history(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Returns the list of all email sending jobs, sorted by creation date.
    """
    jobs = db.query(models.Job).order_by(models.Job.created_at.desc()).all()
    return jobs

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job_detail(
    job_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Returns details for a specific job.
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Session d'envoi non trouvée")
    return job
