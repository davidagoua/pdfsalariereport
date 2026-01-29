from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import zipfile
import os
import uuid
from app.models.schemas import DownloadRequest
from app.core.config import settings
from app.api import deps
from app.models import models

router = APIRouter()

@router.post("/download-zip")
async def download_zip(
    request: DownloadRequest,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Creates a ZIP file containing the requested PDFs.
    """
    if not request.files:
        raise HTTPException(status_code=400, detail="No files selected")
        
    zip_filename = f"bulletins_{uuid.uuid4()}.zip"
    zip_path = os.path.join(settings.TEMP_DIR, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in request.files:
            file_path = os.path.join(settings.COMPLETED_DIR, filename)
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=filename)
                
    return FileResponse(zip_path, filename="bulletins.zip", media_type="application/zip")
