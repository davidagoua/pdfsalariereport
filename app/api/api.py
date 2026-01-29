
from fastapi import APIRouter
from app.api.endpoints import preview, send, download, auth

api_router = APIRouter()

api_router.include_router(preview.router, tags=["preview"])
api_router.include_router(send.router, tags=["send"])
api_router.include_router(download.router, tags=["download"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
