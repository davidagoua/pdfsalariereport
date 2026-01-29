
from sqlalchemy.orm import Session
from app.models import models
import logging

logger = logging.getLogger(__name__)

def sync_employees_data(db: Session, processed_data: list):
    """
    Syncs employees and documents to the database from the processed data list.
    """
    for item in processed_data:
        if item["status"] != "TROUVE":
            continue
            
        matricule = item["id"] # This is the matricule from service
        email = item["email"]
        name = item["name"]
        filename = item["filename"]
        path = item["path"]
        
        # Heuristic to get period from filename if not available elsewhere
        # e.g. "01 HERVE KOFFI BULLETIN DE SALAIRE SEPT25"
        import re
        period_match = re.search(r'BULLETIN DE SALAIRE\s+(.*)', filename)
        period = period_match.group(1).replace(".pdf", "") if period_match else "UNKNOWN"

        # 1. Sync Employee
        employee = db.query(models.Employee).filter(models.Employee.matricule == matricule).first()
        if not employee:
            employee = models.Employee(
                matricule=matricule,
                name=name,
                email=email
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
        else:
            # Update info if changed
            employee.name = name
            employee.email = email
            db.commit()

        # 2. Add Document
        # Check if this document (employee+period) already exists
        doc = db.query(models.EmployeeDocument).filter(
            models.EmployeeDocument.employee_id == employee.id,
            models.EmployeeDocument.period == period
        ).first()
        
        if not doc:
            doc = models.EmployeeDocument(
                employee_id=employee.id,
                filename=filename,
                period=period,
                path=path
            )
            db.add(doc)
            db.commit()
        else:
            # Update path if it already exists (re-processing)
            doc.filename = filename
            doc.path = path
            db.commit()

    logger.info(f"Synchronized {len(processed_data)} employee process entries.")
