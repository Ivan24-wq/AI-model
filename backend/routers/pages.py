from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

def safe_file(name: str):
    file = FRONTEND_DIR / name
    if not file.exists():
        return JSONResponse(
            status_code=400,
            content={"error": f"{name} no found"}
        )
    return FileResponse(file)


router = APIRouter()

@router.get("/")
def root():
    return safe_file("index.html")

@router.get("/register.html")
def register():
    return safe_file("register.html")

@router.get("/reset_confirm.html")
def reset_page():
    return safe_file("frontend/reset_confirm.html")