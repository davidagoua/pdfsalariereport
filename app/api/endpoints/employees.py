
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.api import deps
from app.models import models, schemas
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[schemas.EmployeeResponse])
def get_employees(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    employees = db.query(models.Employee).all()
    
    # Heuristic: attach the latest document to each employee
    results = []
    for emp in employees:
        emp_data = schemas.EmployeeResponse.from_orm(emp)
        # Get latest document
        latest_doc = db.query(models.EmployeeDocument).filter(
            models.EmployeeDocument.employee_id == emp.id
        ).order_by(models.EmployeeDocument.created_at.desc()).first()
        
        if latest_doc:
            emp_data.latest_document = schemas.EmployeeDocumentResponse.from_orm(latest_doc)
        
        results.append(emp_data)
        
    return results

@router.get("/{employee_id}/download/{document_id}")
def download_employee_document(
    employee_id: str,
    document_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    doc = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.id == document_id,
        models.EmployeeDocument.employee_id == employee_id
    ).first()
    
    if not doc or not os.path.exists(doc.path):
        raise HTTPException(status_code=404, detail="Document non trouvé")
        
    return FileResponse(
        doc.path, 
        filename=doc.filename, 
        media_type="application/pdf"
    )
