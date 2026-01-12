
from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import logging
from app.core.config import settings
from app.utils.excel_parser import parse_excel
from app.services.pdf_service import process_pdf_splits

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/preview")
async def preview_processing(pdf_file: UploadFile = File(...), excel_file: UploadFile = File(...)):
    """
    1. Saves uploaded files.
    2. Parses Excel for mapping.
    3. Splits PDF and tries to match employees.
    4. Returns a list of employees/files for the user to review.
    """
    try:
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
        # We process splits directly to the completed dir to be ready for sending
        processed_data = process_pdf_splits(pdf_path, employee_map, settings.COMPLETED_DIR)
        
        return {
            "status": "success",
            "total_pages": len(processed_data),
            "data": processed_data
        }

    except Exception as e:
        logger.error(f"Error in preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
