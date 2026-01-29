from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import shutil
import os
import logging
from app.core.config import settings
from app.utils.excel_parser import parse_excel
from app.services.pdf_service import process_pdf_splits
from app.services.employee_service import sync_employees_data
from app.core.database import SessionLocal
from app.api import deps
from app.models import models

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/preview")
async def preview_pdf(
    pdf_file: UploadFile = File(...),
    excel_file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    1. Saves uploaded files.
    2. Parses Excel for mapping.
    3. Splits PDF and tries to match employees.
    4. Syncs results to Employee table.
    5. Returns a list of employees/files for review.
    """
    try:
        # Ensure temp dir exists
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        os.makedirs(settings.COMPLETED_DIR, exist_ok=True)

        # Save files temporarily
        pdf_path = os.path.join(settings.TEMP_DIR, pdf_file.filename)
        excel_path = os.path.join(settings.TEMP_DIR, excel_file.filename)
        
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(pdf_file.file, f)
        with open(excel_path, "wb") as f:
            shutil.copyfileobj(excel_file.file, f)
            
        # Parse Excel
        employee_map = parse_excel(excel_path)
        logger.info(f"Loaded {len(employee_map)} employees from Excel.")
        
        # Process PDF
        processed_data = process_pdf_splits(pdf_path, employee_map, settings.COMPLETED_DIR)
        
        # Sync Employees and Documents to DB
        db = SessionLocal()
        try:
            sync_employees_data(db, processed_data)
        except Exception as sync_error:
            logger.error(f"Sync error: {sync_error}")
        finally:
            db.close()

        return {
            "status": "success",
            "total_pages": len(processed_data),
            "data": processed_data
        }

    except Exception as e:
        logger.error(f"Error in preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
