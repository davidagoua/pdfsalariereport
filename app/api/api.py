
from fastapi import APIRouter
from app.api.endpoints import preview, send, download, auth, employees, history

api_router = APIRouter()

api_router.include_router(preview.router, tags=["preview"])
api_router.include_router(send.router, tags=["send"])
api_router.include_router(download.router, tags=["download"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
