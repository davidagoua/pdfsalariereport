from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import uuid
import os
import logging
from typing import List
from app.api import deps
from app.models import models, schemas
from app.services.email_service import send_email
from app.core.database import SessionLocal 
from app.models.models import Job, EmailLog 

router = APIRouter()
logger = logging.getLogger(__name__)

def process_email_batch(job_id: str, recipients: List[schemas.EmployeeSelection], subject: str, body: str):
    """
    Background task to process emails and update DB.
    We create a NEW session here because this runs in a background thread.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting email batch job {job_id} for {len(recipients)} recipients.")
        
        # Get Job from DB
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in background task!")
            return

        for recipient in recipients:
            log_entry = EmailLog(job_id=job_id, recipient_email=recipient.email, filename=recipient.filename)
            
            # Verify file existence
            if not os.path.exists(recipient.path):
                log_entry.status = "failed"
                log_entry.error_message = "File not found"
                db.add(log_entry)
                db.commit()
                continue
                
            if not recipient.email:
                 log_entry.status = "skipped"
                 log_entry.error_message = "No email provided"
                 db.add(log_entry)
                 db.commit()
                 continue

            # Send Email
            try:
                success = send_email(
                    to_email=recipient.email,
                    subject=subject,
                    body=body,
                    attachment_paths=[recipient.path]
                )
                log_entry.status = "sent" if success else "failed"
                if not success:
                    log_entry.error_message = "SMTP Error"
            except Exception as e:
                log_entry.status = "failed"
                log_entry.error_message = str(e)
            
            db.add(log_entry)
            db.commit()

        job.status = "completed"
        db.commit()
        logger.info(f"Job {job_id} completed.")
        
    except Exception as e:
        logger.error(f"Error in background task: {e}")
        # Try to mark job as failed
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                db.commit()
        except:
            pass
    finally:
        db.close()

@router.post("/send")
async def send_emails(
    request: schemas.SendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Triggers background email sending. Returns a Job ID.
    Job is created in DB immediately.
    """
    job_id = str(uuid.uuid4())
    
    # Create Job record
    new_job = Job(id=job_id, status="processing")
    db.add(new_job)
    db.commit()
    
    background_tasks.add_task(
        process_email_batch, 
        job_id, 
        request.recipients, 
        request.subject, 
        request.body
    )
    
    return {"job_id": job_id, "status": "processing"}

@router.get("/status/{job_id}")
async def get_status(
    job_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Returns the status of a background job from DB.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Construct response matching previous format
    # details needs to be list of dicts
    details = []
    for log in job.email_logs:
        details.append({
            "email": log.recipient_email,
            "status": log.status,
            "error": log.error_message
        })

    return {
        "status": job.status,
        "details": details
    }
