
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from app.core.config import settings
from app.api.api import api_router
from app.api.endpoints import web
from app.core.database import engine, Base
from app.core.auth_middleware import AuthMiddleware

# Create Tables
Base.metadata.create_all(bind=engine)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Salarié API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

# API Routes
app.include_router(api_router, prefix="/api")
app.include_router(web.router)


app.mount("/files", StaticFiles(directory=settings.COMPLETED_DIR), name="files")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
