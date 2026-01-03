
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

from fastapi import BackgroundTasks
import uuid

# Memory storage for job results
# Format: { job_id: { "status": "processing"|"completed", "details": [ {id, status, error} ] } }
jobs_db = {}

def process_email_batch(job_id: str, recipients: List[EmployeeSelection], subject: str, body: str):
    """
    Background task to process emails.
    """
    results = []
    logger.info(f"Starting email batch job {job_id} for {len(recipients)} recipients.")
    
    for recipient in recipients:
        result_entry = {"id": recipient.id, "email": recipient.email}
        
        # Verify file existence
        if not os.path.exists(recipient.path):
            result_entry["status"] = "failed"
            result_entry["error"] = "File not found"
            results.append(result_entry)
            continue
            
        if not recipient.email:
             result_entry["status"] = "skipped"
             result_entry["error"] = "No email provided"
             results.append(result_entry)
             continue

        # Send Email
        success = send_email(
            to_email=recipient.email,
            subject=subject,
            body=body,
            attachment_paths=[recipient.path]
        )
        
        result_entry["status"] = "sent" if success else "failed"
        results.append(result_entry)
        
        # Update job progress in real-time (optional, here we just append)
        jobs_db[job_id]["details"] = results

    jobs_db[job_id]["status"] = "completed"
    logger.info(f"Job {job_id} completed.")

@app.post("/api/send")
async def send_emails_background(request: SendRequest, background_tasks: BackgroundTasks):
    """
    Triggers background email sending. Returns a Job ID.
    """
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {
        "status": "processing",
        "details": []
    }
    
    background_tasks.add_task(
        process_email_batch, 
        job_id, 
        request.recipients, 
        request.subject, 
        request.body
    )
    
    return {"job_id": job_id, "status": "processing"}

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """
    Returns the status of a background job.
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return jobs_db[job_id]

from fastapi.responses import FileResponse
import zipfile

class DownloadRequest(BaseModel):
    files: List[str]

@app.post("/api/download-zip")
async def download_zip(request: DownloadRequest):
    """
    Creates a ZIP file containing the requested PDFs.
    """
    if not request.files:
        raise HTTPException(status_code=400, detail="No files selected")
        
    zip_filename = f"bulletins_{uuid.uuid4()}.zip"
    zip_path = os.path.join(TEMP_DIR, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in request.files:
            file_path = os.path.join(COMPLETED_DIR, filename)
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=filename)
                
    return FileResponse(zip_path, filename="bulletins.zip", media_type="application/zip")

# Serve Static Files (Frontend)
app.mount("/files", StaticFiles(directory=COMPLETED_DIR), name="files")
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
