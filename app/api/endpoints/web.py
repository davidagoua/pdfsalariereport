
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core.templates import templates

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/salaries", response_class=HTMLResponse)
async def read_salaries(request: Request):
    return templates.TemplateResponse("salaries.html", {"request": request})

@router.get("/historique", response_class=HTMLResponse)
async def read_historique(request: Request):
    return templates.TemplateResponse("historique.html", {"request": request})

@router.get("/parametres", response_class=HTMLResponse)
async def read_parametres(request: Request):
    return templates.TemplateResponse("parametres.html", {"request": request})
