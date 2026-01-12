
from fastapi import APIRouter
from app.api.endpoints import preview, send, download

api_router = APIRouter()

api_router.include_router(preview.router, tags=["preview"])
api_router.include_router(send.router, tags=["send"])
api_router.include_router(download.router, tags=["download"])
