
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
import os
import logging
from typing import List

from app.utils.excel_parser import parse_excel
from app.services.pdf_service import process_pdf_splits
from app.services.email_service import send_email

# Verify imports work
# Uvicorn entry point

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
ASSETS_DIR = "/Users/macbookpro/devspace/pdfsalarie/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)
TEMP_DIR = os.path.join(ASSETS_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
COMPLETED_DIR = os.path.join(ASSETS_DIR, "completed")
os.makedirs(COMPLETED_DIR, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class EmployeeSelection(BaseModel):
    id: str
    name: str # Optional for verification
    email: str
    filename: str
    path: str

class SendRequest(BaseModel):
    recipients: List[EmployeeSelection]
    subject: str = "Votre Bulletin de salaire"
    body: str = "Bonjour M ,Mme veuillez trouver en pièces vos bulletins de salaire .Bonne réception .Hervé KOFFI"

@app.post("/api/preview")
async def preview_processing(pdf_file: UploadFile = File(...), excel_file: UploadFile = File(...)):
    """
    1. Saves uploaded files.
    2. Parses Excel for mapping.
    3. Splits PDF and tries to match employees.
    4. Returns a list of employees/files for the user to review.
    """
    try:
        # Save files temporarily
        pdf_path = os.path.join(TEMP_DIR, pdf_file.filename)
        excel_path = os.path.join(TEMP_DIR, excel_file.filename)
        
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(pdf_file.file, f)
        with open(excel_path, "wb") as f:
            shutil.copyfileobj(excel_file.file, f)
            
        # Parse Excel
        employee_map = parse_excel(excel_path)
        logger.info(f"Loaded {len(employee_map)} employees from Excel.")
        
        # Process PDF
        # We process splits directly to the completed dir to be ready for sending
        # Or maybe keep in temp until sent? Let's use COMPLETED_DIR as 'Staging Area'
        processed_data = process_pdf_splits(pdf_path, employee_map, COMPLETED_DIR)
        
        return {
            "status": "success",
            "total_pages": len(processed_data),
            "data": processed_data
        }

    except Exception as e:
        logger.error(f"Error in preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send")
async def send_emails(request: SendRequest):
    """
    Iterates over the selected recipients and sends emails.
    """
    results = []
    for recipient in request.recipients:
        
        # Verify file existence
        file_path = recipient.path
        if not os.path.exists(file_path):
            results.append({"id": recipient.id, "status": "failed", "error": "File not found"})
            continue
            
        if not recipient.email:
             results.append({"id": recipient.id, "status": "skipped", "error": "No email provided"})
             continue

        # Send Email
        success = send_email(
            to_email=recipient.email,
            subject=request.subject,
            body=request.body,
            attachment_paths=[file_path]
        )
        
        results.append({
            "id": recipient.id,
            "status": "sent" if success else "failed",
            "email": recipient.email
        })
        
    return {"results": results}

# Serve Static Files (Frontend)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
