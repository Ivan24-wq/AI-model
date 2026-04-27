from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from routers import pages

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend"
)

app.include_router(pages.router)